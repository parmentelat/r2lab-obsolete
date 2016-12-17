"""
The PLCAPI version of the view that answers xhttp requests about users
"""

from django.http import HttpResponse

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from plc.plcapiview import PlcApiView
import plc.xrn

# Create your views here.
class UsersProxy(PlcApiView):
    """
    The view that receives /users/ URLs when running agains a PlCAPI
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
                return self.get_users(record)
            else:
                return self.http_response_from_struct(
                    {'error' : "Unknown verb {}".format(verb)})
        except Exception as exc:
            return self.http_response_from_struct(
                {'error' : "Failure when running verb {}".format(verb),
                 'message' : exc})


    def user_with_accounts(self, plc_person, slices_index):
        """
        given a person record as retrned by plc
        and a hash of slices hashed on their slice_id
        we rebuild a record that looks like what omf used to return
        """
        omflike_record = {
            'uuid' : plc_person['person_id'],
            'urn' : plc.xrn.type_hrn_to_urn('user', plc_person['hrn']),
            'email' : plc_person['email'],
            # hopefully useless :
            # 'resource_type' : 'user'
            }
        def plc_slice_account(plc_slice):
            """
            rebuild an omf-like account record
            """
            return {'name' : plc_slice['name'],
                    # hopefully useless
                    # 'resource_type', 'urn', 'created_at'
                    'uuid': plc_slice['slice_id'],
                    'valid_until': self.epoch_to_ui_ts(plc_slice['expires']),
                   }
        # convert all related slices into accounts
        omflike_record['accounts'] = [
            plc_slice_account(slices_index[slice_id])
            for slice_id in plc_person['slice_ids']
            ]
        return omflike_record

    def get_users(self, record):
        """
        retrieve user objects

        If 'urn' is provided in the input record, it should contain a
        URN and only this one will be returned

        otherwise all users are returned
        """
        error = self.check_record(record, (), ('urn', ))
        if error:
            return self.http_response_from_struct(error)
        self.init_plcapi_proxy()

        # compute plc_filter 
        if 'urn' in record:
            type, hrn = plc.xrn.urn_to_type_hrn(record['urn'])
            hrn2 = hrn.replace('onelab.', 'r2lab.', 1)
            plc_filter = { 'hrn' : [hrn, hrn2] }
        else:
            plc_filter = {}

        person_columns = ['person_id', 'email', 'hrn', 'slice_ids']
        persons = self.plcapi_proxy.GetPersons(plc_filter, person_columns)
        # remove persons without an hrn
        persons = [p for p in persons if p['hrn']]

        # build a second call to grab all slices of interest
        all_slice_ids = sum( (p['slice_ids'] for p in persons), [])
        slice_columns = ['slice_id', 'name', 'hrn', 'expires']
        slices = self.plcapi_proxy.GetSlices(all_slice_ids, slice_columns)
        # hash on slice_id
        slices_index = { slice['slice_id']: slice for slice in slices }
        return self.http_response_from_struct(
            [self.user_with_accounts(person, slices_index)
             for person in persons])
