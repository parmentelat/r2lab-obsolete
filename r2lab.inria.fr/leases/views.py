import asyncio
import json
import uuid

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

    def return_lease(self, lease):
        """
        what to return upon ADD or UPDATE
        """
        return {'uuid' : lease['uuid'],
                'slicename' : lease['account']['name'],
                'valid_from' : lease['valid_from'],
                'valid_until' : lease['valid_until'],
                'ok' : OmfSfaProxy.is_accepted_lease(lease),
            }

    #################### ADD
    def add_lease(self, record):
        error = self.check_record(record,
                                  ('slicename', 'valid_from', 'valid_until'), ())
        if error:
            return self.http_response_from_struct(error)
        self.init_omf_sfa_proxy()
        js = self.loop.run_until_complete(self.co_add_lease(record))
        try:
            result = json.loads(js)
            lease = result['resource_response']['resource']
            return self.http_response_from_struct(
                self.return_lease(lease))
        except:
            import traceback
            traceback.print_exc()
            return self.http_response_from_struct(
                {'error': 'unexpected error',
                 'raw_result' : js,
             })

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
        
        logger.info("-> omf_sfa POST request {}".format(lease_request))
        result = yield from self.omf_sfa_proxy.REST_as_json("leases", "POST", lease_request)
        logger.info("omf_sfa POST -> {}".format(result))
        return result

    #################### UPDATE
    def update_lease(self, record):
        error = self.check_record(record,
                                  ('uuid',), ('valid_from', 'valid_until'))
        if error:
            return self.http_response_from_struct(error)
        self.init_omf_sfa_proxy()
        js = self.loop.run_until_complete(self.co_update_lease(record))
        try:
            result = json.loads(js)
            lease = result['resource_response']['resource']
            return self.http_response_from_struct(
                self.return_lease(lease))
        except:
            import traceback
            traceback.print_exc()
            return self.http_response_from_struct(
                {'error': 'unexpected error',
                 'raw_result' : js,
             })

    @asyncio.coroutine
    def co_update_lease(self, record):
        lease_request = record
        logger.info("-> omf_sfa PUT request {}".format(lease_request))
        result = yield from self.omf_sfa_proxy.REST_as_json("leases", "PUT", lease_request)
        logger.info("omf_sfa PUT -> {}".format(result))
        return result

        
    #################### DELETE
    def delete_lease(self, record):
        error = self.check_record(record, ('uuid',), ())
        if error:
            return self.http_response_from_struct(error)
        self.init_omf_sfa_proxy()
        js = self.loop.run_until_complete(self.co_delete_lease(record))
        try:
            result = json.loads(js)
            ok = result['resource_response']['response']
            return self.http_response_from_struct(
                {'ok' : ok=="OK"})
        except:
            import traceback
            traceback.print_exc()
            return self.http_response_from_struct(
                {'error': 'unexpected error',
                 'raw_result' : js,
             })

    @asyncio.coroutine
    def co_delete_lease(self, record):
        lease_request = record
        logger.info("-> omf_sfa DELETE request {}".format(lease_request))
        result = yield from self.omf_sfa_proxy.REST_as_json("leases", "DELETE", lease_request)
        logger.info("omf_sfa DELETE -> {}".format(result))
        return result
