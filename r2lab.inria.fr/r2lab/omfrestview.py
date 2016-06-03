import os.path
import json
import asyncio

from django.http import HttpResponse

from django.views.generic import View

# essentially, this describes the OMF REST API endpoint details
from r2lab.settings import omfrest_settings, logger

### the standard way to use rhubarbe is to have it installed separately
try:
    from rhubarbe.omfsfaproxy import OmfSfaProxy
# in a standalone / devel environment however, just create a symlink
except:
    from .omfsfaproxy import OmfSfaProxy

class OmfRestView(View):

    def not_authenticated_error(self, request):
        """
        The error to return as-is if user is not authenticated
        """
        if 'r2lab_context' not in request.session or \
          'mfuser' not in request.session['r2lab_context']:
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

    # xxx all the hard-wired data here needs to become configurable
    # we want to leverage the code from rhubarbe that does all this
    # but asynchroneously
    # we need to create a loop object for each hit on this URL
    # asyncio does create a loop object (get_event_loop())
    # but this is attached to main thread, it's not usable in this context
    # xxx we might need to do some cleanup on loops at some point 
    def init_omf_sfa_proxy(self):
        self.loop = asyncio.new_event_loop()
        # we use this location on r2lab.inria.fr which is readable by apache
        self.omf_sfa_proxy \
            = OmfSfaProxy(omfrest_settings['hostname'],
                          omfrest_settings['port'],
                          omfrest_settings['root_pem'], None,
                          omfrest_settings['nodename'],
                          loop=self.loop)

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

    def normalize_responses(self, responses):
        """
        for concurrent calls
        sometimes one method uses several ways to achieve its operation
        like e.g. get_slices, that would send
        * either ONE request for the whole list of accounts
        * OR several individual requests, one per account

        our job here is to remove the 'resource_response' step so that all results
        are homogeneous and look like a list of the actual resource records
        """

        try:
            return responses[0]['resource_response']['resources'] 
        except KeyError:
            return [response['resource_response']['resource'] for response in responses]

    # error checking what comes back from omf-sfa
    def rain_check(self, post_result, action):
        """
        returns a tuple value, error
        if error is set, it should be returned as an http response
        otherwise value is guaranteed to have a 'resource_response' field
        """
        if not post_result:
            return None, self.http_response_from_struct(
                {'error' : "Could not {}".format(action)})
        try:
            parsed = json.loads(post_result)
        except Exception as e:
            return None, self.http_response_from_struct(
                {'error' : str(e)})
        if 'resource_response' not in parsed:
            return None, self.http_response_from_struct({'error' : parsed})
        return parsed, None

        
