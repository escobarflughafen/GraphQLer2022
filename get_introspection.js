function intuneGetToken() {

  const requestUrl = "http://neogeek.io:4000/graphql?";
  var options = {};
  var payload = JSON.stringify({
    "query": "\n    query IntrospectionQuery {\n      __schema {\n        \n        queryType { name }\n        mutationType { name }\n        subscriptionType { name }\n        types {\n          ...FullType\n        }\n        directives {\n          name\n          description\n          \n          locations\n          args {\n            ...InputValue\n          }\n        }\n      }\n    }\n\n    fragment FullType on __Type {\n      kind\n      name\n      description\n      \n      fields(includeDeprecated: true) {\n        name\n        description\n        args {\n          ...InputValue\n        }\n        type {\n          ...TypeRef\n        }\n        isDeprecated\n        deprecationReason\n      }\n      inputFields {\n        ...InputValue\n      }\n      interfaces {\n        ...TypeRef\n      }\n      enumValues(includeDeprecated: true) {\n        name\n        description\n        isDeprecated\n        deprecationReason\n      }\n      possibleTypes {\n        ...TypeRef\n      }\n    }\n\n    fragment InputValue on __InputValue {\n      name\n      description\n      type { ...TypeRef }\n      defaultValue\n      \n      \n    }\n\n    fragment TypeRef on __Type {\n      kind\n      name\n      ofType {\n        kind\n        name\n        ofType {\n          kind\n          name\n          ofType {\n            kind\n            name\n            ofType {\n              kind\n              name\n              ofType {\n                kind\n                name\n                ofType {\n                  kind\n                  name\n                  ofType {\n                    kind\n                    name\n                  }\n                }\n              }\n            }\n          }\n        }\n      }\n    }\n  ",
    
  });
  options.method = "post";
  options.contentType = "application/json";
  options.payload = payload;
  
  var response = 0;
  try {
    response = UrlFetchApp.fetch(requestUrl, options);
  } catch(e) {
    Logger.log(e);
  }

  var results = JSON.parse(response.getContentText());

  var inputObjectList = [];
  var objectList = [];
  var scalarList = [];
  var enumList = [];
  var queryList = [];
  var mutationList = [];

  var queryTypeName = results.data.__schema.queryType.name;
  var mutationTypeName = results.data.__schema.mutationType.name;

  var typeData = results.data.__schema.types;

  typeData.forEach(function (d, i) {
    if(d.kind == "INPUT_OBJECT"){
      let object = {};
      object.name = d.name;
      object.inputFields = d.inputFields;
    }else if(d.kind == "OBJECT"){
      if(d.name == queryTypeName){
        d.fields.forEach(function(d,i){
          let object = {};
          object.name = d.name;
          object.type = d.type;
          object.args = [];
          d.args.forEach(function(d,i){
            let arg = {};
            arg.name = d.name;
            object.args.push(arg);
          });
          queryList.push(object);
        })
      }else if(d.name == mutationTypeName){
        d.fields.forEach(function(d,i){
          let object = {};
          object.name = d.name;
          object.type = d.type;
          object.args = [];
          d.args.forEach(function(d,i){
            let arg = {};
            arg.name = d.name;
            object.args.push(arg);
          });
          mutationList.push(object);
        })
      }else{
        let object = {};
        d.fields.forEach(function(d,i){
          object.name = d.name;
          object.type = d.type.kind;
        })
        objectList.push(object);
      }
    }else if(d.kind == "SCALAR"){
      scalarList.push(d);
    }else if(d.kind == "ENUM"){
      enumList.push(d);
    }
  });

  return results;

}
