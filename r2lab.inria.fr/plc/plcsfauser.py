# essentially, this describes the PLCAPI endpoint details
from r2lab.settings import plcapi_settings, logger

from plc.plcapiview import init_plcapi_proxy, PlcApiView

import plc.xrn


##########
# this is a quick and dirty copy of the method
# in the same name in plc/plcapi_users.py

def user_with_accounts(plc_person, slices_index):
    """
    given a person record as returned by plc
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
                'uuid': plc_slice['slice_id'],
                'valid_until': PlcApiView.epoch_to_ui_ts(plc_slice['expires']),
        }
    # convert all related slices into accounts
    omflike_record['accounts'] = [
        plc_slice_account(slices_index[slice_id])
        for slice_id in plc_person['slice_ids']
    ]
    omflike_record['accounts'].sort(
        key = lambda slice: slice['name'])
    return omflike_record

def get_r2lab_user(hrn):
    """
    This function retrieves at the omf.omf-sfa db the list of slices
    that a user is attached to, together with all the attached details 
    """

    plcapi = init_plcapi_proxy()
    plc_filter = {'hrn' : hrn}
    columns = ['person_id', 'email', 'slice_ids', 'hrn']
    person = plcapi.GetPersons(plc_filter, columns)[0]

    slices = plcapi.GetSlices( {'slice_id' : person['slice_ids']},
                               ['name', 'expires', 'slice_id'])
    slices_index = { s['slice_id'] : s for s in slices }

    return user_with_accounts(person, slices_index)
