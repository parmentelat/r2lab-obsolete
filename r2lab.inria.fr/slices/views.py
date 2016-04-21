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
from r2lab.omfrestview import OmfRestView

# Create your views here.
class SlicesProxy(OmfRestView):

    @method_decorator(csrf_protect)
    def post(self, request, verb):
        auth_error = self.not_authenticated_error(request)
        if auth_error:
            return auth_error
        # otherwise
        record = self.decode_body_as_json(request)
        if verb == 'get':
            return self.get_slices(record)
        else:
            return self.http_response_from_struct(
                {'error' : "Unknown verb {}".format(verb)})

    def get_slices(self, record):
        """
        retrieve account objects
        if 'names' is provided in the input record, it should contain a 
        list of slicenames (hrns) and only these will be probed then
        otherwise all slices are returned
        """
        error = self.check_record(record, (), ('names', ))
        if error:
            return self.http_response_from_struct(error)
        self.init_omf_sfa_proxy()
        if 'names' in record:
            # issue all requests in parallel
            jobs = [
                self.co_get_slice(slicename) for slicename in record['names']
            ]
            js_s = self.loop.run_until_complete(asyncio.gather(*jobs, loop=self.loop))
        else:
            js_s = [ self.loop.run_until_complete(self.co_get_slice()) ]
        try:
            responses = [ json.loads(js) for js in js_s ]
            responses = self.normalize_responses(responses)
            responses = [ response for response in responses if
                          response['name'] not in ('__default__',) ]
            responses.sort(key=lambda r: r['name'])
            return self.http_response_from_struct(responses)
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.exception("Cannot get slices")
            return self.http_response_from_struct(
                { 'error': 'unexpected error',
                  'raw_result' : js_s,
              })

    @asyncio.coroutine
    def co_get_slice(self, slicename=None):
        url = "accounts" if slicename is None else "account?name={}".format(slicename)
        js = yield from self.omf_sfa_proxy.REST_as_json(url, "GET", None)
        return js

