import json
import os, os.path
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import View
from django.http import HttpResponse
from datetime import datetime

# Create your views here.
class FilesProxy(View):

    def http_response_from_struct(self, answer):
        return HttpResponse(json.dumps(answer))

    def not_authenticated_error(self, request):
        """
        The error to return as-is if user is not authenticated
        """
        if 'r2lab_context' not in request.session or \
          'mfuser' not in request.session['r2lab_context']:
            return self.http_response_from_struct(
                {'error' : 'User is not authenticated'})

    def decode_body_as_json(self, request):
        utf8 = request.body.decode()
        return json.loads(utf8)

    # @method_decorator(csrf_protect)
    def post(self, request, verb):
        # auth_error = self.not_authenticated_error(request)
        # if auth_error:
        #     return auth_error
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
        directory = os.path.dirname(os.path.abspath(__file__))
        directory = directory+'/nightly/'
        data      = []

        if record['file'] == 'nigthly':
            the_file  = 'nightly_data.json'
            try:
                with open(directory + the_file) as f:
                    for line in f:
                        temp_line = self.remove_issue_after_maintenance(line)
                        data.append(json.loads(temp_line))
                    f.close()
                    return self.http_response_from_struct(data)
            except Exception as e:
                return self.http_response_from_struct(
                    { 'error' : "Failure running get file",
                      'message' : e})
        else:
            return self.http_response_from_struct(
                { 'error' : "File not found or not alowed" })


    def remove_issue_after_maintenance(self, line):
        """
        remove elements after maintenance to send to the page the data after maintenance
        'node' : 'maintenance date'
        """
        directory = os.path.dirname(os.path.abspath(__file__))
        directory = directory+'/nightly/'
        the_file  = 'maintenance_nodes.json'
        data      = []

        try:
            with open(directory + the_file) as data_file:
                maintenance_nodes = json.load(data_file)
            #LOAD JSON WHEN IS EACH LINE A JSON DB
            # data = []
            # with open(directory + the_file) as fi:
            #     for linex in fi:
            #         data.append(json.loads(linex))
            #     fi.close()
        except Exception as e:
            print("Failure in read maintenance file - {} - {} - {}".format(directory, the_file, e))

        element = json.loads(line)
        for el in maintenance_nodes:
            for date in maintenance_nodes[el]:
                try:
                    avoid_date = datetime.strptime(date, "%Y-%m-%d")
                    based_date = datetime.strptime(element['date'], "%Y-%m-%d")
                    if(based_date <= avoid_date):
                        element['data'].pop(el)

                except Exception as e:
                    pass

        return json.dumps(element)
