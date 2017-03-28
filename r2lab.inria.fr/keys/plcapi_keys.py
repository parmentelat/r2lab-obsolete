"""
The PLCAPI version of the view that answers xhttp requests about keys
"""

from django.http import HttpResponse

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from plc.plcapiview import PlcApiView
import plc.xrn

# Create your views here.
class KeysProxy(PlcApiView):
    """
    The view that receives /keys/ URLs when running agains a PlCAPI
    """

    @method_decorator(csrf_protect)
    def post(self, request, verb):
        """
        xhtp requests come using a POST http command
        """
        auth_error = self.not_authenticated_error(request)
        if auth_error:
            return auth_error

        email = request.session['r2lab_context']['user_details']['email']
        try:
            record = self.decode_body_as_json(request)
            if verb == 'get':
                return self.get_keys(record, email)
            elif verb == 'add':
                return self.add_key(record, email)
            elif verb == 'delete':
                return self.delete_key(record, email)
            else:
                return self.http_response_from_struct(
                    {'error' : "Unknown verb {}".format(verb)})
        except Exception as exc:
            return self.http_response_from_struct(
                {'error' : "Failure when running verb {}".format(verb),
                 'message' : exc})

    def get_person_id(self, email):
        if hasattr(self, '_person_id'):
            return self._person_id
        self.init_plcapi_proxy()
        persons = self.plcapi_proxy.GetPersons(
            {'email' : email},
            ['email', 'person_id'])
        self._person_id = persons[0]['person_id']
        return self._person_id

    def get_keys(self, record, email):
        """
        incoming record is a json record for consistency
        but is ignored in this call as the actual PLCAPI person
        used for filtering keys is deduced from the logged in session
        """
        self.init_plcapi_proxy()
        person_id = self.get_person_id(email)
        plc_filter = {'person_id' : person_id}
        keys = self.plcapi_proxy.GetKeys(plc_filter)
        return self.http_response_from_struct(keys)

    def add_key(self, record, email):
        error = self.check_record(record, ('key',), ())
        if error:
            return self.http_response_from_struct(error)
        self.init_plcapi_proxy()
        # the actual key contents - not a file !
        key = record['key']
        new_key_id = self.plcapi_proxy.AddPersonKey(
            email, {'key_type' : 'ssh', 'key' : key})
        return self.http_response_from_struct(
            {'uuid' : new_key_id})

    def delete_key(self, record, email):
        error = self.check_record(record, ('uuid',), ())
        if error:
            return self.http_response_from_struct(error)
        self.init_plcapi_proxy()
        retcod = self.plcapi_proxy.DeleteKey(record['uuid'])
        return self.http_response_from_struct(
            {'ok' : retcod == 1})
