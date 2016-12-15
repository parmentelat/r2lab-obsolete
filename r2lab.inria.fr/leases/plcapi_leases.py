"""
The PLCAPI version of the view that answers xhttp requests about leases
"""

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

# importing PlcApiProxy through this module because of the symlink hack
from plc.plcapiview import PlcApiView


class LeasesProxy(PlcApiView):
    """
    The view that receives /leases/ URLs when running agains a PlCAPI
    """

    @method_decorator(csrf_protect)
    def post(self, request, verb):
        """
        xhtp requests come using a POST http command
        """
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
                    {'error': "Unknown verb {}".format(verb)})
        except Exception as exc:
            import traceback
            traceback.print_exc()
            return self.http_response_from_struct(
                {'error': "Failure when running verb {}".format(verb),
                 'message': exc})

    def return_lease(self, plc_lease):
        """
        what to return upon ADD or UPDATE
        """
        return {'uuid': plc_lease['lease_id'],
                'slicename': plc_lease['name'],
                'valid_from': self.epoch_to_ui_ts(plc_lease['t_from']),
                'valid_until': self.epoch_to_ui_ts(plc_lease['t_until']),
                'ok': True}

    def add_lease(self, record):
        """
        propagates a request to add lease to PCLAPI
        """
        error = self.check_record(
            record,
            ('slicename', 'valid_from', 'valid_until'), ())
        if error:
            return self.http_response_from_struct(error)
        self.init_plcapi_proxy()
        unique_hostname = self.unique_component_name()
        retcod = self.plcapi_proxy.AddLeases(
            [unique_hostname], self.ensure_plc_slicename(record['slicename']),
            self.ui_ts_to_plc_ts(record['valid_from']),
            self.ui_ts_to_plc_ts(record['valid_until']))
        if retcod['errors']:
            return self.http_response_from_struct({'error': '\n'.join(retcod['errors'])})
        # only one lease gets created
        lease_id = retcod['new_ids'][0]
        # go back to the API to get limits - possibly rectified wrt granularity
        lease = self.plcapi_proxy.GetLeases(lease_id)[0]
        response = self.http_response_from_struct(self.return_lease(lease))
        return response

    def update_lease(self, record):
        """
        propagates a request to update lease to PCLAPI
        """
        error = self.check_record(record,
                                  ('uuid',), ('valid_from', 'valid_until'))
        if error:
            return self.http_response_from_struct(error)
        self.init_plcapi_proxy()
        lease_id = record['uuid']
        retcod = self.plcapi_proxy.UpdateLeases(
            [lease_id],
            {'t_from': self.ui_ts_to_plc_ts(record['valid_from']),
             't_until': self.ui_ts_to_plc_ts(record['valid_until'])})
        if retcod['errors']:
            self.http_response_from_struct(
                {'error': '\n'.join(retcod['errors'])})
        # go back to the API to get limits - possibly rectified wrt granularity
        lease = self.plcapi_proxy.GetLeases(lease_id)[0]
        response = self.http_response_from_struct(self.return_lease(lease))
        return response

    def delete_lease(self, record):
        """
        propagates a request to delete lease to PCLAPI
        """
        error = self.check_record(record, ('uuid',), ())
        if error:
            return self.http_response_from_struct(error)
        lease_id = record['uuid']
        self.init_plcapi_proxy()
        retcod = self.plcapi_proxy.DeleteLeases([lease_id])
        return self.http_response_from_struct(
            {'ok': retcod == 1})
