use cpython::{Python, PyDict, PyResult, PyObject, PyBool, PyErr, exc, PyList, PyString};
use pact_verifier::{PactSource, FilterInfo, VerificationOptions, ProviderInfo};
use log::*;
use url::Url;
use ansi_term::Colour::*;
use pact_verifier::callback_executors::{RequestFilterExecutor, ProviderStateExecutor, ProviderStateError};
use std::sync::Arc;
use pact_matching::models::Request;
use std::collections::HashMap;
use serde_json::Value;
use pact_matching::models::provider_states::ProviderState;
use async_trait::async_trait;
use regex::Regex;
use maplit::*;

pub(crate) fn setup_provider_config(
  py: Python,
  provider: &str,
  base_url: &str,
  kwargs: &PyDict
) -> PyResult<(ProviderInfo, Vec<PactSource>, VerificationOptions<PythonRequestFilterExecutor>, FilterInfo, Vec<String>)>  {
  let mut provider_info = ProviderInfo {
    name: provider.to_string(),
    .. ProviderInfo::default()
  };

  match Url::parse(base_url) {
    Ok(url) => {
      provider_info.protocol = url.scheme().into();
      provider_info.host = url.host_str().unwrap_or("localhost").into();
      provider_info.port = url.port();
      provider_info.path = url.path().into();
    },
    Err(err) => {
      error!("Failed to parse base_url: {}", err);
      println!("    {}", Red.paint("ERROR: base_url is not a valid URL"));
      return Err(PyErr::new::<exc::AttributeError, _>(py, format!("Failed to parse base_url: {}", err)));
    }
  };

  let mut pacts: Vec<PactSource> = vec![];
  dbg!(kwargs.len(py));
  if let Some(pact_urls) = kwargs.get_item(py, "sources") {
    if let Ok(pact_urls) = pact_urls.cast_as::<PyList>(py) {
      for pact in pact_urls.iter(py) {
        if let Ok(pact) = pact.cast_as::<PyString>(py) {
          let pact_str = pact.to_string_lossy(py);
          let re = Regex::new(r"^\w+://").unwrap();
          if dbg!(re.is_match(pact_str.as_ref())) {
            pacts.push(PactSource::URL(pact_str.to_string(), None))
          } else {
            pacts.push(PactSource::File(pact_str.to_string()))
          }
        } else {
          println!("    {}", Yellow.paint (format!("WARN: pact_url '{}' is not a valid URL string", pact)))
        }
      }
    } else {
      println!("    {}", Yellow.paint ("WARN: pact_urls does not contain a valid list of URL strings"))
    }
  }

  // let provider_tags = match get_string_array(&mut cx, &config, "providerVersionTags") {
  //   Ok(tags) => tags,
  //   Err(e) => return cx.throw_error(e)
  // };
  //
  // match config.get(&mut cx, "pactBrokerUrl") {
  //   Ok(url) => match url.downcast::<JsString>() {
  //     Ok(url) => {
  //       let pending = get_bool_value(&mut cx, &config, "enablePending");
  //       let wip = get_string_value(&mut cx, &config, "includeWipPactsSince");
  //       let consumer_version_tags = match get_string_array(&mut cx, &config, "consumerVersionTags") {
  //         Ok(tags) => tags,
  //         Err(e) => return cx.throw_error(e)
  //       };
  //       let selectors = consumer_tags_to_selectors(consumer_version_tags);
  //
  //       if let Some(username) = get_string_value(&mut cx, &config, "pactBrokerUsername") {
  //         let password = get_string_value(&mut cx, &config, "pactBrokerPassword");
  //         pacts.push(PactSource::BrokerWithDynamicConfiguration { provider_name: provider.clone(), broker_url: url.value(), enable_pending: pending, include_wip_pacts_since: wip, provider_tags: provider_tags.clone(), selectors: selectors, auth: Some(HttpAuth::User(username, password)), links: vec![] })
  //       } else if let Some(token) = get_string_value(&mut cx, &config, "pactBrokerToken") {
  //         pacts.push(PactSource::BrokerWithDynamicConfiguration { provider_name: provider.clone(), broker_url: url.value(), enable_pending: pending, include_wip_pacts_since: wip, provider_tags: provider_tags.clone(), selectors: selectors, auth: Some(HttpAuth::Token(token)), links: vec![] })
  //       } else {
  //         pacts.push(PactSource::BrokerWithDynamicConfiguration { provider_name: provider.clone(), broker_url: url.value(), enable_pending: pending, include_wip_pacts_since: wip, provider_tags: provider_tags.clone(), selectors: selectors, auth: None, links: vec![] })
  //       }
  //     },
  //     Err(_) => {
  //       if !url.is_a::<JsUndefined>() {
  //         println!("    {}", Red.paint("ERROR: pactBrokerUrl must be a string value"));
  //         cx.throw_error("pactBrokerUrl must be a string value")?;
  //       }
  //     }
  //   },
  //   _ => ()
  // };
  //
  // debug!("pacts = {:?}", pacts);
  // if pacts.is_empty() {
  //   println!("    {}", Red.paint("ERROR: No pacts were found to verify!"));
  //   cx.throw_error("No pacts were found to verify!")?;
  // }
  //
  // let mut provider_info = ProviderInfo {
  //   name: provider.clone(),
  //   .. ProviderInfo::default()
  // };
  //
  // match get_string_value(&mut cx, &config, "providerBaseUrl") {
  //   Some(url) => match Url::parse(&url) {
  //     Ok(url) => {
  //       provider_info.protocol = url.scheme().into();
  //       provider_info.host = url.host_str().unwrap_or("localhost").into();
  //       provider_info.port = url.port();
  //       provider_info.path = url.path().into();
  //     },
  //     Err(err) => {
  //       error!("Failed to parse pactBrokerUrl: {}", err);
  //       println!("    {}", Red.paint("ERROR: pactBrokerUrl is not a valid URL"));
  //     }
  //   },
  //   None => ()
  // };
  //
  // debug!("provider_info = {:?}", provider_info);
  //
  // let callback_timeout = get_integer_value(&mut cx, &config, "callbackTimeout").unwrap_or(5000);
  //
  // let request_filter = match config.get(&mut cx, "requestFilter") {
  //   Ok(request_filter) => match request_filter.downcast::<JsFunction>() {
  //     Ok(val) => {
  //       let this = cx.this();
  //       Some(Arc::new(RequestFilterCallback {
  //         callback_handler: EventHandler::new(&cx, this, val),
  //         timeout: callback_timeout
  //       }))
  //     },
  //     Err(_) => None
  //   },
  //   _ => None
  // };
  //
  // debug!("request_filter done");
  //
  // let mut callbacks = hashmap![];
  // match config.get(&mut cx, "stateHandlers") {
  //   Ok(state_handlers) => match state_handlers.downcast::<JsObject>() {
  //     Ok(state_handlers) => {
  //       let this = cx.this();
  //       let props = state_handlers.get_own_property_names(&mut cx).unwrap();
  //       for prop in props.to_vec(&mut cx).unwrap() {
  //         let prop_name = prop.downcast::<JsString>().unwrap().value();
  //         let prop_val = state_handlers.get(&mut cx, prop_name.as_str()).unwrap();
  //         if let Ok(callback) = prop_val.downcast::<JsFunction>() {
  //           callbacks.insert(prop_name, EventHandler::new(&cx, this, callback));
  //         }
  //       };
  //     },
  //     Err(_) => ()
  //   },
  //   _ => ()
  // };
  //
  // let publish = match config.get(&mut cx, "publishVerificationResult") {
  //   Ok(publish) => match publish.downcast::<JsBoolean>() {
  //     Ok(publish) => publish.value(),
  //     Err(_) => {
  //       warn!("publishVerificationResult must be a boolean value. Ignoring it");
  //       false
  //     }
  //   },
  //   _ => false
  // };
  //
  // let provider_version = match config.get(&mut cx, "providerVersion") {
  //   Ok(provider_version) => match provider_version.downcast::<JsString>() {
  //     Ok(provider_version) => Some(provider_version.value().to_string()),
  //     Err(_) => if !provider_version.is_a::<JsUndefined>() {
  //       println!("    {}", Red.paint("ERROR: providerVersion must be a string value"));
  //       return cx.throw_error("providerVersion must be a string value")
  //     } else {
  //       None
  //     }
  //   },
  //   _ => None
  // };
  //
  // if publish && provider_version.is_none() {
  //   println!("    {}", Red.paint("ERROR: providerVersion must be provided if publishing verification results in enabled (publishVerificationResult == true)"));
  //   return cx.throw_error("providerVersion must be provided if publishing verification results in enabled (publishVerificationResult == true)")?
  // }
  //
  // let disable_ssl_verification = match config.get(&mut cx, "disableSSLVerification") {
  //   Ok(disable) => match disable.downcast::<JsBoolean>() {
  //     Ok(disable) => disable.value(),
  //     Err(_) => {
  //       if !disable.is_a::<JsUndefined>() {
  //         warn!("disableSSLVerification must be a boolean value. Ignoring it");
  //       }
  //       false
  //     }
  //   },
  //   _ => false
  // };

  let filter_info = FilterInfo::None;
  let consumers_filter: Vec<String> = vec![];
  let options = VerificationOptions {
    // publish,
    // provider_version,
    // build_url: None,
    // request_filter,
    // provider_tags,
    // disable_ssl_verification,
    // callback_timeout,
    .. VerificationOptions::default()
  };
  Ok((provider_info, pacts, options, filter_info, consumers_filter))
}

pub(crate) struct PythonRequestFilterExecutor;

impl RequestFilterExecutor for PythonRequestFilterExecutor {
  fn call(self: Arc<Self>, request: &Request) -> Request {
    unimplemented!()
  }
}

pub(crate) struct PythonProviderStateExecutor;

impl PythonProviderStateExecutor {
  pub(crate) fn new() -> PythonProviderStateExecutor {
    PythonProviderStateExecutor {}
  }
}

#[async_trait]
impl ProviderStateExecutor for PythonProviderStateExecutor {
  async fn call(self: Arc<Self>, interaction_id: Option<String>, provider_state: &ProviderState, setup: bool, client: Option<&reqwest::Client>) -> Result<HashMap<String, Value>, ProviderStateError> {
    Ok(hashmap!{})
  }
}
