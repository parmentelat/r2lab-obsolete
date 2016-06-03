import asyncio
import json
import uuid

from django.shortcuts import render

from django.http import HttpResponse

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from r2lab.settings import logger
# importing OmfSfaProxy through this module because of the symlink hack
from r2lab.omfrestview import OmfRestView, OmfSfaProxy

# Create your views here.
class LeasesProxy(OmfRestView):

    @method_decorator(csrf_protect)
    def post(self, request, verb):
        auth_error = self.not_authenticated_error(request)
        if auth_error:
            return auth_error
        # otherwise
        try:
            record = self.decode_body_as_json(request)
            if verb == 'add':
                return self.add_lease(record)
            elif verb == 'update':
                return self.update_lease(record)
            elif verb == 'delete':
                return self.delete_lease(record)
            else:
                return self.http_response_from_struct(
                    {'error' : "Unknown verb {}".format(verb)})
        except Exception as e:
            return self.http_response_from_struct(
                { 'error' : "Failure when running verb {}".format(verb),
                  'message' : e})

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
        post_result = self.loop.run_until_complete(self.co_add_lease(record))
        result, error = self.rain_check(post_result, "add lease")
        if error:
            return error
        lease = result['resource_response']['resource']
        return self.http_response_from_struct(
            self.return_lease(lease))

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
        post_result = self.loop.run_until_complete(self.co_update_lease(record))
        result, error = self.rain_check(post_result, "update lease")
        if error:
            return error
        lease = result['resource_response']['resource']
        return self.http_response_from_struct(
            self.return_lease(lease))

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
        post_result = self.loop.run_until_complete(self.co_delete_lease(record))
        result, error = self.rain_check(post_result, "delete lease")
        if error:
            return error
        ok = result['resource_response']['response']
        return self.http_response_from_struct(
            {'ok' : ok=="OK"})

    @asyncio.coroutine
    def co_delete_lease(self, record):
        lease_request = record
        logger.info("-> omf_sfa DELETE request {}".format(lease_request))
        result = yield from self.omf_sfa_proxy.REST_as_json("leases", "DELETE", lease_request)
        logger.info("omf_sfa DELETE -> {}".format(result))
        return result
