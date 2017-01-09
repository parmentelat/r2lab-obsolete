#
# this is a virtual layer created while migrating from
# omf-sfa to plcapi
#
# historically we had OmfRestView that did the job of interacting with
# omf-sfa using REST, and so there was a need to slit this in 2 parts
# 
# it would have made sense to call this r2labapiview, but r2labapi
# is the hostname for the VM that runs the PLCAPI for r2lab
# so this name is tainted towards plcapi
#

import json

from django.http import HttpResponse

from django.views.generic import View

class TestbedApiView(View):
    
    def not_authenticated_error(self, request):
        """
        The error to return as-is if user is not authenticated
        """
        if 'r2lab_context' not in request.session or \
          'user_details' not in request.session['r2lab_context']:
            return self.http_response_from_struct(
                {'error' : 'User is not authenticated'})
        

    def decode_body_as_json(self, request):
        utf8 = request.body.decode()
        return json.loads(utf8)
    
    def http_method_not_allowed(self, request):
        env = {'previous_message' : 'HTTP method not allowed'}
        return md.views.markdown_page(request, 'oops', env)
    
    # JSON encode and wrap into a HttpResponse
    def http_response_from_struct(self, answer):
        return HttpResponse(json.dumps(answer))

    def check_record(self, record, mandatory, optional):
        """
        checks for the keys in the input record
        
        returns None if everything is OK
        and an error message otherwise
        """
        missing = { k for k in mandatory if k not in record }
        known = set(mandatory) | set(optional)
        unknown = { k for k in record if k not in known }
        error = ""
        if missing:
            error += "missing mandatory field(s): {}".format(" ".join(missing))
        if unknown:
            error += " unknown field(s): {}".format(" ".join(unknown))
        return None if not error else {'error' : error}

