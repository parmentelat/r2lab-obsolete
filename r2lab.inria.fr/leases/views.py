import asyncio
import json
import uuid

from django.shortcuts import render

from django.views.generic import View

from django.http import HttpResponse

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

try:
    from rhubarbe.omfsfaproxy import OmfSfaProxy
except:
    from .omfsfaproxy import OmfSfaProxy

# Create your views here.
class LeasesProxy(View):

    # this URL supports only POST
    def http_method_not_allowed(self, request):
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
        print("/leases/ received verb={} and record {}".format(verb, record))
        if verb == 'add':
            return self.add_lease(record)
        elif verb == 'update':
            return self.update_lease(record)
        elif verb == 'delete':
            return self.delete_lease(record)
        else:
            return self.http_response_from_struct(
                {'error' : "Unknown verb {}".format(verb)})

    # JSON encode and wrap into a HttpResponse
    def http_response_from_struct(answer):
        return HttpResponse(json.dumps(answer))

    # xxx all the hard-wired data here needs to become configurable
    # we want to leverage the code from rhubarbe that does all this
    # but asynchroneously
    # we need to create a loop object for each hit on this URL
    # asyncio does create a loop object (get_event_loop())
    # but this is attached to main thread, it's not usable in this context
    def init_omf_sfa_proxy(self):
        self.loop = asyncio.new_event_loop()
        # xxx we might need to do some cleanup on loops at some point 
        self.omf_sfa_proxy \
            = OmfSfaProxy("faraday.inria.fr", 12346,
                          "/root/.omf/user_cert.pem", None,
                          "37nodes",
                          loop=self.loop)

    def missing_message(self, record, keys):
        missing = [ k for k in keys if k not in record ]
        if missing:
            return {'error': "missing mandatory field(s)".format(" ".join(missing))}

    def add_lease(self, record):
        error = self.missing_message(
            record,
            ['slicename', 'valid_from', 'valid_until'])
        if error:
            return self.http_response_from_struct(error)
        self.init_omf_sfa_proxy()
        result = self.loop.run_until_complete(self.co_add_lease(record))
        print ("add_lease complete, result = {}",format(result))
#        del loop
        return self.http_response_from_struct(result)

    @asyncio.coroutine
    def co_add_lease(self, record):
        node_uuid = yield from self.omf_sfa_proxy.fetch_node_uuid()
        lease_request = {
            'name' : str(uuid.uuid1()),
            'valid_from' : record['valid_from'],
            'valid_until' : record['valid_until'],
            'account_attributes' : { 'name' : record['slicename'] },
            'components' : [ {'uuid' : node_uuid } ],
            }
        result = yield from self.omf_sfa_proxy.REST_as_json("leases", "POST", lease_request)
        return result

