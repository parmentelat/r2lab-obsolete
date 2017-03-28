"""
The PLCAPI version of the view that answers xhttp requests about slices
"""

import time

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

# importing PlcApiProxy through this module because of the symlink hack
from plc.plcapiview import PlcApiView

# Create your views here.


class SlicesProxy(PlcApiView):
    """
    The view that receives /slices/ URLs when running against a PLCAPI
    """

    @method_decorator(csrf_protect)
    def post(self, request, verb):
        """
        xhtp requests come using a POST http command
        """
        auth_error = self.not_authenticated_error(request)
        if auth_error:
            return auth_error
        try:
            record = self.decode_body_as_json(request)
            if verb == 'get':
                return self.get_slices(record)
            if verb == 'renew':
                return self.renew_slice(record)
            else:
                return self.http_response_from_struct(
                    {'error': "Unknown verb {}".format(verb)})
        except Exception as exc:
            import traceback
            traceback.print_exc()
            return self.http_response_from_struct(
                {'error': "Failure when running verb {}".format(verb),
                 'message': exc})

    def return_slice(self, plc_slice):
        """
        what to return upon ADD or UPDATE
        """
        return {'name': plc_slice['name'],
                'valid_until': self.epoch_to_ui_ts(plc_slice['expires'])}

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
        self.init_plcapi_proxy()
        columns = [
            'slice_id', 'name', 'expires'
        ]
        # compute filter based on whether names are specified
        if 'names' not in record:
            plc_filter = {}
        else:
            plc_names = [self.ensure_plc_slicename(name)
                         for name in record['names']]
            plc_names = [x for x in plc_names if x]
            if not plc_names:
                return self.http_response_from_struct([])
            plc_filter = { 'name' : plc_names }
        plc_slices = self.plcapi_proxy.GetSlices(
            plc_filter, columns
        )
        slices = [self.return_slice(plc_slice)
                  for plc_slice in plc_slices]
        slices.sort(key=lambda slice: slice['valid_until'])
        return self.http_response_from_struct(slices)

    def renew_slice(self, record):
        """
        renew a slice

        * mandatory argument is 'name' that should hold a valid hrn
        * optional argument is 'valid_until' that should then in the
          omf-sfa timestamp format
          if not provided the slice is renewed until 2 months from now
        """
        error = self.check_record(record,
                                  ('name',), ('valid_until',))
        if error:
            return self.http_response_from_struct(error)
        if 'valid_until' in record:
            expires = self.ui_ts_to_epoch(record['valid_until'])
        else:
            day = 24 * 3600
            # 2 months is 61 days
            expires = int(time.time()) + 61 * day

        self.init_plcapi_proxy()
        plc_slice_name = self.ensure_plc_slicename(record['name'])
        retcod = self.plcapi_proxy.UpdateSlice(
            plc_slice_name,
            {'expires': expires}
        )
        if retcod == 1:
            # go back to plcapi to get fresh status
            slices_now = self.plcapi_proxy.GetSlices(
                plc_slice_name
            )
            return self.http_response_from_struct(
                self.return_slice(slices_now[0]))
        else:
            return self.http_response_from_struct(
                {'error': "Could not renew slice {}"
                 .format(record['name'])})
