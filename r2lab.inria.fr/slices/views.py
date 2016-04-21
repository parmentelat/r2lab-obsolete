from django.shortcuts import render

# Create your views here.

import asyncio
import json

from django.shortcuts import render

from django.views.generic import View

from django.http import HttpResponse

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from r2lab.settings import logger

### the standard way to use rhubarbe is to have it installed separately
try:
    from rhubarbe.omfsfaproxy import OmfSfaProxy
# in a standalone environment however, just create a symlink:
except:
    from .omfsfaproxy import OmfSfaProxy

# Create your views here.
class SlicesProxy(View):

    # this URL supports only POST
    def http_method_not_allowed(self, *request):
        print("request=", request)
        env = {'previous_message' : 'HTTP method not allowed'}
        return md.views.markdown_page(request, 'oops', env)
    
    @method_decorator(csrf_protect)
    def post(self, request, verb):
        # not authenticated
        if 'r2lab_context' not in request.session or \
          'mfuser' not in request.session['r2lab_context']:
            return self.http_response_from_struct(
                {'error' : 'User is not authenticated'})
        # otherwise
        utf8 = request.body.decode()
        record = json.loads(utf8);
        if verb == 'get':
            return self.get_slices(record)
        else:
            return self.http_response_from_struct(
                {'error' : "Unknown verb {}".format(verb)})

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
            = OmfSfaProxy("faraday.inria.fr", 12346,
                          "/etc/rhubarbe/root.pem", None,
                          "37nodes",
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


    def get_slices(self, record):
        """
        retrieve the account objects attached to a list of slicenames
        """
        error = self.check_record(record,
                                  ('names', ),
                                  ())
        if error:
            return self.http_response_from_struct(error)
        self.init_omf_sfa_proxy()
        # issue all requests in parallel
        jobs = [
            self.co_get_slice(slicename) for slicename in record['names']
            ]
        print("-> gather jobs", jobs)
        js_s = self.loop.run_until_complete(asyncio.gather(*jobs, loop=self.loop))
        try:
            results = [ json.loads(js) for js in js_s ]
            return self.http_response_from_struct(results)
        except:
            import traceback
            traceback.print_exc()
            return self.http_response_from_struct(
                { 'error': 'unexpected error',
                  'raw_result' : js_s,
              })

    @asyncio.coroutine
    def co_get_slice(self, slicename):
        url = "account?name={}".format(slicename)
        logger.debug("-> omf_sfa GET on url {}".format(url))
        js = yield from self.omf_sfa_proxy.REST_as_json(url, "GET", None)
        logger.info("<- omf_sfa GET {}".format(js))
        return js
