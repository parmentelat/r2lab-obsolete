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
        try:
            record = self.decode_body_as_json(request)
            if verb == 'get':
                return self.get_slices(record)
            else:
                return self.http_response_from_struct(
                    {'error' : "Unknown verb {}".format(verb)})
        except Exception as e:
            return self.http_response_from_struct(
                { 'error' : "Failure when running verb {}".format(verb),
                  'message' : e})


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
        ######## if names are specified
        if 'names' in record:
            # issue all requests in parallel
            jobs = [
                self.co_get_slice(slicename) for slicename in record['names']
            ]
            # we already have a list
            js_s = self.loop.run_until_complete(asyncio.gather(*jobs, loop=self.loop))
            responses = [ json.loads(js) for js in js_s ]
            slices = [ response['resource_response']['resource']
                       for response in responses ]
        ######## retrieve all slices in one shot
        else:
            js = self.loop.run_until_complete(self.co_get_slice())
            response = json.loads(js)
            slices = response['resource_response']['resources']
            slices = [ slice for slice in slices
                       if slice['name'] not in ('__default__', ) ]
            # temporary - should be handled in the UI
            slices.sort(key=lambda r: r['valid_until'])

        return self.http_response_from_struct(slices)

    @asyncio.coroutine
    def co_get_slice(self, slicename=None):
        url = "accounts" if slicename is None else "account?name={}".format(slicename)
        js = yield from self.omf_sfa_proxy.REST_as_json(url, "GET", None)
        return js

