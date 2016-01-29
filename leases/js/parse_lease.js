$(document).ready(function() {

  function parseLease(url) {
    $.getJSON(url, function(data) {
        var jsonObj = [];
        $.each(data, function(key,val){
          $.each(val.resource_response.resources, function(k,v){
            var title, start, end, color;

            title = v.account.name;
            start = v.valid_from;
            end   = v.valid_until;
            if (v.resource_type === 'lease') {
              color = '#257e4a';
            }

            newJson = new Object();
            newJson.title = title;
            newJson.start = start;
            newJson.end   = end;
            newJson.color = color;

            jsonObj.push(newJson);
          });
        });
        return in_json(jsonObj);
    });
  }

  function in_json(object) {
    new_json = JSON.stringify(object);
    return new_json;
  }

  function main() {
    parseLease('/leases_original');
  }

  main();

});
