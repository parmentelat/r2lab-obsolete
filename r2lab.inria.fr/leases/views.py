import json

from django.shortcuts import render

from django.views.generic import View

from django.http import HttpResponse

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

# Create your views here.
class LeasesProxy(View):

    @method_decorator(csrf_protect)
    def post(self, request):
        # not authenticated
        if 'r2lab_context' not in request.session or \
          'mfuser' not in request.session['r2lab_context']:
            answer = {'error' : 'User is not authenticated'}
            return HttpResponse(json.dumps(answer))
        # otherwise
        utf8 = request.body.decode()
        record = json.loads(utf8);
        print("/leases/ received record {}".format(record))
        # to be continued from here
        if 'action' not in record:
            answer = {'error' : 'missing action'}
            return HttpResponse(json.dumps(answer))
        action = record['action']
        if action.lower() == 'add':
            if 'slicename' not in record:
                answer = {'error' : 'add lease : missing slicename'}
                return HttpResponse(json.dumps(answer))
        slicename = record['slicename']
        username = request.session['r2lab_context']['mfuser']
        # need to craft another record, send it upwards to omf_sfa
        # and return some result
        # completely fake for now
        answer = {'code' : 100, 'message' : "about to perform action {}".format(action)}
        return HttpResponse(json.dumps(answer))

    def http_method_not_allowed(self, request):
        env = {'previous_message' : 'HTTP method not allowed'}
        return md.views.markdown_page(request, 'oops', env)
    
