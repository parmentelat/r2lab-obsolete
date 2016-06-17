import json
import os, os.path

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

# importing OmfSfaProxy through this module because of the symlink hack
from r2lab.omfrestview import OmfRestView, OmfSfaProxy

# Create your views here.
class FilesProxy(OmfRestView):

    @method_decorator(csrf_protect)
    def post(self, request, verb):
        auth_error = self.not_authenticated_error(request)
        if auth_error:
            return auth_error
        try:
            record = self.decode_body_as_json(request)
            if verb == 'get':
                return self.get_file(record)
            else:
                return self.http_response_from_struct(
                    {'error' : "Unknown verb {}".format(verb)})
        except Exception as e:
            return self.http_response_from_struct(
                { 'error' : "Failure when running verb {}".format(verb),
                  'message' : e})



    def get_file(self, record):
        """
        return nigthly routine file in json format
        """
        directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prev_dir, dir = os.path.split(directory)

        #/root/r2lab/nightly (real place)
        directory = prev_dir+'/nightly/'
        data      = []

        if record['file'] == 'nigthly':
            the_file  = 'nightly_data.json'

        with open(directory + the_file) as f:
            for line in f:
                print(line)
                data.append(json.loads(line))

        return self.http_response_from_struct(data)
