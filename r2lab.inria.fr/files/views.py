import json
import os, os.path
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import View
from django.http import HttpResponse
from datetime import datetime
import markdown2

# Create your views here.
class FilesProxy(View):

    def http_response_from_struct(self, answer):
        return HttpResponse(json.dumps(answer))

    def not_authenticated_error(self, request):
        """
        The error to return as-is if user is not authenticated
        """
        if 'r2lab_context' not in request.session or \
          'user_details' not in request.session['r2lab_context']:
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
                return self.which_file(record)
            else:
                return self.http_response_from_struct(
                    {'error' : "Unknown verb {}".format(verb)})
        except Exception as e:
            return self.http_response_from_struct(
                { 'error' : "Failure when running verb {}".format(verb),
                  'message' : e})

    def which_file(self, record):
        """
        return nigthly routine file in json format
        """
        option = record['file']
        if option == 'nigthly':
            return self.get_nigthly()
        elif option == 'detail':
            return self.get_detail()
        elif int(option['info']) in list(range(1,38)):
            node = option['info']
            return self.get_info(node)
        else:
            return self.http_response_from_struct(
                { 'error' : "File not found or not alowed" })

    def get_detail(self):
        """
        return nodes details in json format
        """
        directory    = os.path.dirname(os.path.abspath(__file__))
        directory    = directory+'/nodes/'
        the_file     = 'table_nodes.json'
        try:
            with open(directory + the_file) as data_file:
                data = json.load(data_file)
            data = self.build_detail(data)
            return self.http_response_from_struct(data)
        except Exception as e:
            data = {}
            print("Failure in read node detail file - {} - {} - {}".format(directory, the_file, e))
            return self.http_response_from_struct(data)

    def get_nigthly(self):
        """
        return nodes infos in json format
        """
        directory = os.path.dirname(os.path.abspath(__file__))
        directory = directory+'/nightly/'
        data      = []
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

    def build_detail(self, data):
        """
        parse image to <img src> and md to html
        """
        directory = os.path.dirname(os.path.abspath(__file__))
        directory = directory+'/nodes/'
        images   = ['.jpg', '.jpeg', '.png']
        content  = ['.md']
        new_data = data

        for dt in data:
            for d in data[dt]:
                file  = d['value']
                ftype = os.path.splitext(file)[1]

                if ftype.lower() in content:
                    try:
                        with open(directory + file) as f:
                            lines = f.readlines()
                            lines = ('').join([markdown2.markdown(x.rstrip()) for x in lines])
                            d['value'] = lines
                            f.close()
                        d['value'] = '<div class="in_md">{}</div>'.format(d['value'])
                    except Exception as e:
                        pass
                elif ftype.lower() in images:
                    # img_tag     = '<img src="files/nodes/{}" alt="" style="cursor: pointer;" alt="click to enlarge" width="60" onclick=show_image("files/nodes/{}");>'.format(file, file)
                    img_tag     = '<a href="javascript: return();" alt="click to enlarge" onclick=show_image("files/nodes/{}");><span class="glyphicon glyphicon-camera" style="font-size: 1.3em;"  aria-hidden="true"></span></a>'.format(file, file)
                    d['value']  = img_tag
        return new_data

    def build_node_info(self, node):
        """
        find the node info throught the files already saved
        """
        directory = os.path.dirname(os.path.abspath(__file__))
        directory = directory+'/nodes/'
        data      = False
        setup_file= 'info_nodes.json'
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

    def remove_issue_after_maintenance(self, line):
        """
        remove elements after maintenance to send to the page the data after maintenance
        'node' : 'maintenance date'
        """
        directory = os.path.dirname(os.path.abspath(__file__))
        directory = directory+'/nodes/'
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
            maintenance_nodes = {}
            print("Failure in read maintenance file - {} - {} - {}".format(directory, the_file, e))

        element = json.loads(line)
        for el in maintenance_nodes:
            for item in maintenance_nodes[el]:
                try:
                    avoid_date = datetime.strptime(item['date'], "%Y-%m-%d")#maintenance nodes date
                    based_date = datetime.strptime(element['date'], "%Y-%m-%d")#database
                    if(based_date <= avoid_date and item['reset'] == 'yes'):
                        element['data'].pop(el)

                except Exception as e:
                    pass

        return json.dumps(element)
