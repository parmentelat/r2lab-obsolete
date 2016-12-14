import json
import asyncio

from django.http import HttpResponse

from r2lab.testbedapiview import TestbedApiView

# essentially, this describes the OMF REST API endpoint details
from r2lab.settings import omfrest_settings

### the standard way to use rhubarbe is to have it installed separately
try:
    from rhubarbe.omfsfaproxy import OmfSfaProxy
# in a standalone / devel environment however, just create a symlink
except:
    from .omfsfaproxy import OmfSfaProxy

class OmfRestView(TestbedApiView):

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
    def rain_check(self, post_result, action, error_as_http=True):
        """
        returns a tuple value, error
        if error is set, it should be returned as an http response
        otherwise value is guaranteed to have a 'resource_response' field
        
        if error_as_http is True, the error part, when relevant, is a http_response
        otherwise it's just a string
        """
        def wrap_error(error_string):
            return error_string if not error_as_http else \
                self.http_response_from_struct({'error' : error_string})

        if not post_result:
            return None, wrap_error("Could not {}".format(action))
        try:
            parsed = json.loads(post_result)
        except Exception as e:
            return None, wrap_error(str(e))
        if 'resource_response' not in parsed:
            try:
                error = parsed['exception']['reason']
            except:
                error = str(parsed)
            return None, wrap_error(error)
        return parsed, None
