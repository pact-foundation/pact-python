use std::cell::RefCell;
use std::collections::HashMap;
use std::fs;
use std::str::FromStr;
use std::sync::{Mutex, Arc};

use bytes::Bytes;
use cpython::*;
use env_logger::{Builder, Target};
use lazy_static::*;
use log::*;
use maplit::*;
use pact_matching::models::*;
use pact_matching::models::content_types::ContentType;
use pact_matching::models::generators::Generators;
use pact_matching::models::matchingrules::{MatchingRules, MatchingRule, RuleLogic};
use pact_matching::models::provider_states::ProviderState;
use pact_matching::time_utils::generate_string;
use pact_mock_server::mock_server::MockServerConfig;
use pact_mock_server::server_manager::ServerManager;
use pact_mock_server_ffi::bodies::{process_array, process_object};
use serde_json::{json, Value};
use serde_json::map::Map;
use uuid::Uuid;
use crate::verifier::{setup_provider_config, PythonProviderStateExecutor};

mod verifier;

lazy_static! {
  static ref MANAGER: Mutex<ServerManager> = Mutex::new(ServerManager::new());
}

py_module_initializer!(pact_python_v3, |py, m| {
  m.add(py, "__doc__", "Pact Python V3 support (provided by Pact-Rust FFI)")?;
  m.add(py, "init", py_fn!(py, init_lib(*args, **kwargs)))?;
  m.add(py, "generate_datetime_string", py_fn!(py, generate_datetime_string(format: &str)))?;
  m.add(py, "verify_provider", py_fn!(py, verify_provider(*args, **kwargs)))?;
  m.add_class::<PactNative>(py)?;
  Ok(())
});

py_class!(class PactNative |py| {
  data pact: RefCell<RequestResponsePact>;
  data interaction: RefCell<Option<usize>>;
  
  def __new__(_cls, consumer_name: &str, provider_name: &str, version: &str) -> PyResult<PactNative> {
    let mut metadata = RequestResponsePact::default_metadata();
    metadata.insert("pactPython".to_string(), btreemap!{ "version".to_string() => version.to_string() });
    PactNative::create_instance(py, RefCell::new(RequestResponsePact {
      consumer: Consumer { name: consumer_name.to_string() },
      provider: Provider { name: provider_name.to_string() },
      metadata,
      .. RequestResponsePact::default()
    }), RefCell::new(None))
  }

  def given(&self, provider_state: &str, params: &PyDict) -> PyResult<PyObject> {
    let mut provider_state_params = hashmap!{};
    for (key, val) in params.items(py) {
      let pystr = key.cast_as::<PyString>(py)?.to_string_lossy(py);
      provider_state_params.insert(pystr.to_string(), pyobj_to_json(py, &val)?);
    }

    let provider_state = ProviderState {
      name: provider_state.to_string(),
      params: provider_state_params
    };
    
    self.with_current_interaction(py, &|interaction| {
      interaction.provider_states.push(provider_state.clone());
      Ok(py.None())
    })
  }

  def upon_receiving(&self, description: &str) -> PyResult<PyObject> {
    self.with_current_interaction(py, &|interaction| {
      interaction.description = description.to_string();
      Ok(py.None())
    })
  }

  def with_request(&self, method: &str, path, query, headers, body) -> PyResult<PyObject> {
    self.with_current_interaction(py, &|interaction| {
      interaction.request.method = method.to_string();
      
      if let Ok(path) = path.cast_as::<PyString>(py) {
        interaction.request.path = path.to_string_lossy(py).to_string();
      } else {
        // TODO: deal with a matcher
      }

      if let Ok(query) = query.cast_as::<PyDict>(py) {
        let mut query_map = hashmap!{};
        for (k, v) in query.items(py) {
          let k = k.cast_as::<PyString>(py)?.to_string_lossy(py).to_string();
          let v = if let Ok(v) = v.cast_as::<PyString>(py) {
            vec![ v.to_string_lossy(py).to_string() ]
          } else {
            // TODO: deal with a matcher or a list
            vec![]
          };
          query_map.insert(k, v);
        }
        if !query_map.is_empty() {
          interaction.request.query = Some(query_map);
        }
      } else if query.get_type(py).name(py) != "NoneType" {
        return Err(PyErr::new::<exc::TypeError, _>(py, format!("with_request: Query parameters must be supplied as a Dict, got '{}'", query.get_type(py).name(py))));
      }

      if let Ok(headers) = headers.cast_as::<PyDict>(py) {
        let mut header_map = hashmap!{};
        for (k, v) in headers.items(py) {
          let k = k.cast_as::<PyString>(py)?.to_string_lossy(py).to_string();
          let v = if let Ok(v) = v.cast_as::<PyString>(py) {
            vec![ v.to_string_lossy(py).to_string() ]
          } else {
            // TODO: deal with a matcher or a list
            vec![]
          };
          header_map.insert(k, v);
        }
        if !header_map.is_empty() {
          interaction.request.headers = Some(header_map);
        }
      } else if headers.get_type(py).name(py) != "NoneType" {
        return Err(PyErr::new::<exc::TypeError, _>(py, format!("with_request: Headers must be supplied as a Dict, got '{}'", headers.get_type(py).name(py))));
      }

      if let Ok(body) = body.cast_as::<PyDict>(py) {
        let content_type = interaction.request.content_type().unwrap_or_default();
        let body = self.process_body_as_dict(py, body, content_type, &mut interaction.request.matching_rules, &mut interaction.request.generators)?;
        debug!("request body = {}", body.0.str_value());
        interaction.request.body = body.0;
        if let Some(content_type) = body.1 {
          interaction.request.add_header("Content-Type", vec![&content_type]);
        }
      } else if let Ok(body) = body.cast_as::<PyList>(py) {
        let content_type = interaction.request.content_type().unwrap_or_default();
        let body = self.process_body_as_array(py, body, content_type, &mut interaction.request.matching_rules, &mut interaction.request.generators)?;
        debug!("request body = {}", body.0.str_value());
        interaction.request.body = body.0;
        if let Some(content_type) = body.1 {
          interaction.request.add_header("Content-Type", vec![&content_type]);
        }
      } else if let Ok(body) = body.cast_as::<PyString>(py) {
        interaction.request.body = OptionalBody::Present(Bytes::copy_from_slice(body.to_string_lossy(py).as_bytes()),
          interaction.request.content_type());
      } else if body.get_type(py).name(py) != "NoneType" {
        return Err(PyErr::new::<exc::TypeError, _>(py, format!("with_request: '{}' is not an appropriate type for a body", body.get_type(py).name(py))));
      }

      Ok(py.None())
    })
  }

  def add_request_binary_file(&self, content_type: &str, file_path: &str, method: &str, path, query, headers) -> PyResult<PyObject> {
    self.with_current_interaction(py, &|interaction| {
      interaction.request.method = method.to_string();

      if let Ok(path) = path.cast_as::<PyString>(py) {
        interaction.request.path = path.to_string_lossy(py).to_string();
      } else {
        // TODO: deal with a matcher
      }

      if let Ok(query) = query.cast_as::<PyDict>(py) {
        let mut query_map = hashmap!{};
        for (k, v) in query.items(py) {
          let k = k.cast_as::<PyString>(py)?.to_string_lossy(py).to_string();
          let v = if let Ok(v) = v.cast_as::<PyString>(py) {
            vec![ v.to_string_lossy(py).to_string() ]
          } else {
            // TODO: deal with a matcher or a list
            vec![]
          };
          query_map.insert(k, v);
        }
        if !query_map.is_empty() {
          interaction.request.query = Some(query_map);
        }
      } else if query.get_type(py).name(py) != "NoneType" {
        return Err(PyErr::new::<exc::TypeError, _>(py, format!("with_request: Query parameters must be supplied as a Dict, got '{}'", query.get_type(py).name(py))));
      }

      if let Ok(headers) = headers.cast_as::<PyDict>(py) {
        let mut header_map = hashmap!{};
        for (k, v) in headers.items(py) {
          let k = k.cast_as::<PyString>(py)?.to_string_lossy(py).to_string();
          let v = if let Ok(v) = v.cast_as::<PyString>(py) {
            vec![ v.to_string_lossy(py).to_string() ]
          } else {
            // TODO: deal with a matcher or a list
            vec![]
          };
          header_map.insert(k, v);
        }
        if !header_map.is_empty() {
          interaction.request.headers = Some(header_map);
        }
      } else if headers.get_type(py).name(py) != "NoneType" {
        return Err(PyErr::new::<exc::TypeError, _>(py, format!("with_request: Headers must be supplied as a Dict, got '{}'", headers.get_type(py).name(py))));
      }

      let file = fs::read(file_path).map(|data| OptionalBody::Present(Bytes::from(data), None));
      match file {
        Ok(body) => {
          interaction.request.body = body;
          interaction.request.matching_rules.add_category("body").add_rule("$",
            MatchingRule::ContentType(content_type.to_string()), &RuleLogic::And);
          if !interaction.request.has_header(&"Content-Type".to_string()) {
            match interaction.request.headers {
              Some(ref mut headers) => {
                headers.insert("Content-Type".to_string(), vec!["application/octet-stream".to_string()]);
              },
              None => {
                interaction.request.headers = Some(hashmap! { "Content-Type".to_string() => vec!["application/octet-stream".to_string()]});
              }
            }
          };
        },
        Err(err) => {
          error!("Could not load file '{}': {}", file_path, err);
          return Err(PyErr::new::<exc::TypeError, _>(py, format!("add_request_binary_file: could not load binary file - {}'", err)));
        }
      }

      Ok(py.None())
    })
  }

  def will_respond_with(&self, status, headers, body) -> PyResult<PyObject> {
    self.with_current_interaction(py, &|interaction| {
      interaction.response.status = status.extract(py)?;
      
      if let Ok(headers) = headers.cast_as::<PyDict>(py) {
        let mut header_map = hashmap!{};
        for (k, v) in headers.items(py) {
          let k = k.cast_as::<PyString>(py)?.to_string_lossy(py).to_string();
          let v = if let Ok(v) = v.cast_as::<PyString>(py) {
            vec![ v.to_string_lossy(py).to_string() ]
          } else {
            // TODO: deal with a matcher or a list
            vec![]
          };
          header_map.insert(k, v);
        }
        if !header_map.is_empty() {
          interaction.response.headers = Some(header_map);
        }
      } else if headers.get_type(py).name(py) != "NoneType" {
        return Err(PyErr::new::<exc::TypeError, _>(py, format!("with_request: Headers must be supplied as a Dict, got '{}'", headers.get_type(py).name(py))));
      }

      if let Ok(body) = body.cast_as::<PyDict>(py) {
        let content_type = interaction.request.content_type().unwrap_or_default();
        let body = self.process_body_as_dict(py, body, content_type, &mut interaction.response.matching_rules, &mut interaction.response.generators)?;
        debug!("Response body = {}", body.0.str_value());
        interaction.response.body = body.0;
        if let Some(content_type) = body.1 {
          interaction.response.add_header("Content-Type", vec![&content_type]);
        }
      } else if let Ok(body) = body.cast_as::<PyList>(py) {
        let content_type = interaction.request.content_type().unwrap_or_default();
        let body = self.process_body_as_array(py, body, content_type, &mut interaction.response.matching_rules, &mut interaction.response.generators)?;
        debug!("Response body = {}", body.0.str_value());
        interaction.response.body = body.0;
        if let Some(content_type) = body.1 {
          interaction.response.add_header("Content-Type", vec![&content_type]);
        }
      } else if let Ok(body) = body.cast_as::<PyString>(py) {
        interaction.response.body = OptionalBody::Present(Bytes::copy_from_slice(body.to_string_lossy(py).as_bytes()),
          interaction.response.content_type());
      } else if body.get_type(py).name(py) != "NoneType" {
        return Err(PyErr::new::<exc::TypeError, _>(py, format!("will_respond_with: '{}' is not an appropriate type for a body", body.get_type(py).name(py))));
      }

      debug!("Response = {}", interaction.response);
      debug!("Response matching rules = {:?}", interaction.response.matching_rules);
      debug!("Response generators = {:?}", interaction.response.generators);

      Ok(py.None())
    })?;

    let mut interaction = self.interaction(py).borrow_mut();
    *interaction = None;

    Ok(py.None())
  }

  def start_mock_server(&self) -> PyResult<MockServerHandle> {
    let pact = self.pact(py).borrow();
    let mock_server_id = Uuid::new_v4().to_string();
    let config = MockServerConfig::default();
    let port = MANAGER.lock().unwrap().start_mock_server(mock_server_id.clone(), pact.clone(), 0, config)
      .map_err(|err| PyErr::new::<exc::TypeError, _>(py, err))?;

    debug!("start_mock_server: Mock server running on port {}", port);

    MockServerHandle::create_instance(py, mock_server_id, port)
  }
});

impl PactNative {
  fn with_current_interaction(&self, py: Python, callback: &dyn Fn(&mut RequestResponseInteraction) -> PyResult<PyObject>) -> PyResult<PyObject> {
    let mut pact = self.pact(py).borrow_mut();
    let mut index = self.interaction(py).borrow_mut();
    match *index {
      Some(index) => callback(&mut pact.interactions[index]),
      None => {
        let mut interaction = RequestResponseInteraction::default();
        let result = callback(&mut interaction);
        pact.interactions.push(interaction);
        *index = Some(pact.interactions.len() - 1);
        result
      }
    }
  }

  fn process_body_as_dict(
    &self,
    py: Python,
    body: &PyDict,
    content_type: ContentType,
    matching_rules: &mut MatchingRules,
    generators: &mut Generators
  ) -> PyResult<(OptionalBody, Option<String>)> {
    let mut category = matching_rules.add_category("body");
    if content_type.is_json() {
      let body = pyobj_to_json(py, &body.as_object())?;
      let processed = process_object(body.as_object().unwrap(), &mut category,
                                     generators, "$", false, false);
      Ok((OptionalBody::from(processed.to_string()), Some(content_type.to_string())))
    } 
    // DetectedContentType::Xml => Ok(OptionalBody::Present(process_xml(body, category, generators)?)),
    else {
      let body = pyobj_to_json(py, &body.as_object())?;
      let processed = process_object(body.as_object().unwrap(), &mut category,
                                     generators, "$", false, false);
      Ok((OptionalBody::from(processed.to_string()), Some("application/json".to_string())))
    }
  }

  fn process_body_as_array(
    &self,
    py: Python, body: &PyList,
    content_type: ContentType,
    matching_rules: &mut MatchingRules,
    generators: &mut Generators
  ) -> PyResult<(OptionalBody, Option<String>)> {
    let mut category = matching_rules.add_category("body");
    if content_type.is_json() {
      let body = pyobj_to_json(py, &body.as_object())?;
      let processed = process_array(body.as_array().unwrap(), &mut category,
                                    generators, "$", false, false);
      Ok((OptionalBody::from(processed.to_string()), Some(content_type.to_string())))
    }
    // DetectedContentType::Xml => Ok(OptionalBody::Present(process_xml(body, category, generators)?)),
    else {
      let body = pyobj_to_json(py, &body.as_object())?;
      let processed = process_array(body.as_array().unwrap(), &mut category,
                                    generators, "$", false, false);
      Ok((OptionalBody::from(processed.to_string()), Some("application/json".to_string())))
    }
  }
}

py_class!(class MockServerHandle |py| {
  data id: String;
  data port: u16;

  def get_url(&self) -> PyResult<PyString> {
    Ok(PyString::new(py, format!("http://127.0.0.1:{}", self.port(py)).as_str()))
  }

  def get_port(&self) -> PyResult<PyLong> {
    Ok(self.port(py).to_py_object(py))
  }

  def get_id(&self) -> PyResult<PyString> {
    Ok(self.id(py).as_str().to_py_object(py))
  }

  def get_test_result(&self) -> PyResult<PyObject> {
    match MANAGER.lock().unwrap().find_mock_server_by_id(&self.id(py), &|mock_server| mock_server.mismatches()) {
      Some(mismatches) => if mismatches.is_empty() {
        Ok(py.None())
      } else {
        Ok(mismatches.iter().map(|val| json_to_pyobj(py, &val.to_json())).collect::<Vec<PyObject>>().to_py_object(py).into_object())
      },
      None => Err(PyErr::new::<exc::TypeError, _>(py, format!("Could not get the result from the mock server: there is no mock server with id {}", self.id(py))))
    }
  }

  def write_pact_file(&self, pact_dir: &PyObject, overwrite: &PyObject) -> PyResult<PyObject> {
    let dir = if let Ok(pact_dir) = pact_dir.cast_as::<PyString>(py) {
      let pact_dir = pact_dir.to_string_lossy(py).to_string();
      if pact_dir.is_empty() {
        None
      } else {
        Some(pact_dir)
      }
    } else {
      None
    };

    let overwrite = if let Ok(overwrite) = overwrite.cast_as::<PyBool>(py) {
      overwrite.is_true()
    } else {
      false
    };
    match MANAGER.lock().unwrap().find_mock_server_by_id(&self.id(py), &|mock_server| mock_server.write_pact(&dir, overwrite)) {
      Some(result) => result.map(|_| py.None()).map_err(|err| PyErr::new::<exc::TypeError, _>(py, format!("Failed to write pact to file - {}", err))),
      None => Err(PyErr::new::<exc::TypeError, _>(py, format!("Could not get the mock server to write the pact file: there is no mock server with id {}", self.id(py))))
    }
  }
            
  def shutdown(&self) -> PyResult<PyBool> {
    Ok(MANAGER.lock().unwrap().shutdown_mock_server_by_id(self.id(py).to_string()).to_py_object(py))
  }
});

fn init_lib(py: Python, _: &PyTuple, kwargs: Option<&PyDict>) -> PyResult<PyObject> {
  let mut builder = Builder::from_env("LOG_LEVEL");
  builder.target(Target::Stdout);
  if let Some(kwargs) = kwargs {
    if let Some(log_level) = kwargs.get_item(py, "log_level") {
      if let Ok(pystr) = log_level.cast_as::<PyString>(py) {
        builder.filter(None, LevelFilter::from_str(&pystr.to_string_lossy(py)).unwrap());
      }
    }
  }

  if let Ok(_) = builder.try_init() {
    debug!("Initialising Pact native library version {}", env!("CARGO_PKG_VERSION"));
  }

  Ok(py.None())
}

fn generate_datetime_string(py: Python, format: &str) -> PyResult<PyString> {
  generate_string(&format.to_string()).map(|val| val.to_py_object(py)).map_err(|err| PyErr::new::<exc::TypeError, _>(py, err))
}

fn pyobj_to_json(py: Python, val: &PyObject) -> PyResult<Value> {
  if let Ok(pystr) = val.cast_as::<PyString>(py) {
    Ok(Value::String(pystr.to_string_lossy(py).to_string()))
  } else if let Ok(pybool) = val.cast_as::<PyBool>(py) {
    Ok(Value::Bool(pybool.is_true()))
  } else if let Ok(pyfloat) = val.cast_as::<PyFloat>(py) {
    Ok(json!(pyfloat.value(py)))
  } else if val.cast_as::<PyLong>(py).is_ok() {
    let num: i64 = val.extract(py)?;
    Ok(json!(num))
  } else if val.cast_as::<PyInt>(py).is_ok() {
    let num: i32 = val.extract(py)?;
    Ok(json!(num))
  } else if let Ok(pylist) = val.cast_as::<PyList>(py) {
    let mut array = vec![];
    for v in pylist.iter(py) {
      let j = pyobj_to_json(py, &v)?;
      array.push(j);
    }
    Ok(Value::Array(array))
  } else if let Ok(pylist) = val.cast_as::<PyTuple>(py) {
    let mut array = vec![];
    for v in pylist.iter(py) {
      let j = pyobj_to_json(py, &v)?;
      array.push(j);
    }
    Ok(Value::Array(array))
  } else if let Ok(pylist) = val.cast_as::<PySequence>(py) {
    let mut array = vec![];
    for v in pylist.list(py)?.iter(py) {
      let j = pyobj_to_json(py, &v)?;
      array.push(j);
    }
    Ok(Value::Array(array))
  } else if let Ok(pydict) = val.cast_as::<PyDict>(py) {
    let mut map = Map::new();
    for (k, v) in pydict.items(py) {
      let v = pyobj_to_json(py, &v)?;
      let k = k.cast_as::<PyString>(py)?.to_string_lossy(py);
      map.insert(k.to_string(), v);
    }
    Ok(Value::Object(map))
  } else {
    Err(PyErr::new::<exc::TypeError, _>(py, format!("Could not convert Python object to a JSON form - {}", val.get_type(py).name(py))))
  }
}

fn json_to_pyobj(py: Python, val: &Value) -> PyObject {
  match val {
    Value::Null => py.None(),
    Value::Bool(b) => b.to_py_object(py).into_object(),
    Value::Number(n) => if let Some(n) = n.as_u64() {
      n.to_py_object(py).into_object()
    } else if let Some(n) = n.as_i64() {
      n.to_py_object(py).into_object()
    } else {
      n.as_f64().unwrap_or(0.0).to_py_object(py).into_object()
    },
    Value::String(s) => s.as_str().to_py_object(py).into_object(),
    Value::Array(array) => array.iter().map(|item| json_to_pyobj(py, item)).collect::<Vec<PyObject>>().to_py_object(py).into_object(),
    Value::Object(map) => map.iter().map(|(key, value)| (key.clone(), json_to_pyobj(py, value))).collect::<HashMap<String, PyObject>>().to_py_object(py).into_object()
  }
}

fn verify_provider(
  py: Python,
  args: &PyTuple,
  kwargs: Option<&PyDict>
) -> PyResult<PyBool>  {
  let arg1 = args.get_item(py, 0);
  let provider = arg1.cast_as::<PyString>(py)?.to_string_lossy(py);
  let arg2 = args.get_item(py, 1);
  let base_url = arg2.cast_as::<PyString>(py)?.to_string_lossy(py);
  let arg3 = args.get_item(py, 2);
  let options = arg3.cast_as::<PyDict>(py)?;

  debug!("Verifying provider '{}' running at '{}'", provider, base_url);
  let (provider_info, source, options, filter, consumers) = setup_provider_config(py, provider.as_ref(), base_url.as_ref(), options)?;

  debug!("Pact sources = {:?}", source);
  let result = pact_verifier::verify_provider(
    provider_info,
    source,
    filter,
    consumers,
    options,
    &Arc::new(PythonProviderStateExecutor::new())
  );
  debug!("result = {}", result);

  Ok(PyBool::get(py, result))
}
