use cpython::*;
use log::*;
use env_logger::{Builder, Target};
use std::str::FromStr;
use pact_matching::models::*;
use pact_matching::models::provider_states::ProviderState;
use std::cell::RefCell;
use maplit::*;
use serde_json::{Value, json};
use serde_json::map::Map;
use uuid::Uuid;
use lazy_static::*;
use pact_mock_server::server_manager::ServerManager;
use std::sync::Mutex;

lazy_static! {
  static ref MANAGER: Mutex<ServerManager> = Mutex::new(ServerManager::new());
}

py_module_initializer!(pact_python_v3, |py, m| {
  m.add(py, "__doc__", "Pact Python V3 support (provided by Pact-Rust FFI)")?;
  m.add(py, "init", py_fn!(py, init_lib(*args, **kwargs)))?;
  m.add_class::<PactNative>(py)?;
  Ok(())
});

py_class!(class PactNative |py| {
  data pact: RefCell<Pact>;
  data interaction: RefCell<Option<usize>>;
  
  def __new__(_cls, consumer_name: &str, provider_name: &str) -> PyResult<PactNative> {
    PactNative::create_instance(py, RefCell::new(Pact {
      consumer: Consumer { name: consumer_name.to_string() },
      provider: Provider { name: provider_name.to_string() },
      .. Pact::default()
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

  def with_request(&self, method: &str, path: &PyObject, query: &PyObject, headers: &PyObject) -> PyResult<PyObject> {
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

      dbg!(interaction);
      
      Ok(py.None())
    })
  }

  def start_mock_server(&self) -> PyResult<MockServerHandle> {
    let pact = self.pact(py).borrow();
    let mock_server_id = Uuid::new_v4().to_string();
    let port = MANAGER.lock().unwrap().start_mock_server(mock_server_id.clone(), pact.clone(), 0)
      .map_err(|err| PyErr::new::<exc::TypeError, _>(py, err))?;

    debug!("start_mock_server: Mock server running on port {}", port);

    MockServerHandle::create_instance(py, mock_server_id, port)
  }
});

impl PactNative {
  fn with_current_interaction(&self, py: Python, callback: &dyn Fn(&mut Interaction) -> PyResult<PyObject>) -> PyResult<PyObject> {
    let mut pact = self.pact(py).borrow_mut();
    let mut iteraction = self.interaction(py).borrow_mut();
    match *iteraction {
      Some(index) => callback(&mut pact.interactions[index]),
      None => {
        let mut interaction = Interaction::default();
        let result = callback(&mut interaction);
        pact.interactions.push(interaction);
        *iteraction = Some(0);
        result
      }
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
  builder.init();

  debug!("Initialising Pact native library version {}", env!("CARGO_PKG_VERSION"));

  Ok(py.None())
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
