import json
import os, os.path
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import View
from django.http import HttpResponse
from datetime import datetime
import markdown2

# Create your views here.
class NodesProxy(View):

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

    # @method_decorator(csrf_protect)
    def post(self, request, verb):
        # auth_error = self.not_authenticated_error(request)
        # if auth_error:
        #     return auth_error
        try:
            if verb == 'get':
                node = request.body.decode()
                return self.get_info(node)
            else:
                return self.http_response_from_struct(
                    {'error' : "Unknown verb {}".format(verb)})
        except Exception as e:
            return self.http_response_from_struct(
                { 'error' : "Failure when running verb {}".format(verb),
                  'message' : e})

    def get_info(self, node):
        """
        return nodes infos in json format
        """
        try:
            content = self.build_node_info(node)
            return self.http_response_from_struct(content)
        except Exception as e:
            return self.http_response_from_struct(
                { 'error' : "Failure running get file",
                  'message' : e})

    def build_node_info(self, node):
        """
        find the node info throught the files already saved
        """
        directory = os.path.dirname(os.path.abspath(__file__))
        directory = directory+'/'
        data      = False
        setup_file= 'nodes_info.json'
        try:
            with open(directory + setup_file) as f:
                data = json.load(f)
                f.close()
        except Exception as e:
            print("Failure in read node config file - {} - {} - {}".format(directory, setup_file, e))

        if data:
            for dt in data:
                if dt == node:
                    #find the files and serve them
                    tabs = data[dt]
                    for tb, tab in enumerate(tabs):
                        file = tab["file"]
                        if not type(file) is list:
                            try:
                                with open(directory + file) as f:
                                    lines = f.readlines()
                                    lines = ('').join([markdown2.markdown(x.rstrip()) for x in lines])
                                    data[dt][tb]["content"] = lines
                                    f.close()
                            except Exception as e:
                                pass
        return json.dumps(data)
