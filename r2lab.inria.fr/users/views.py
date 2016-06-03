from django.shortcuts import render

# Create your views here.

import asyncio
import json
import time

from django.shortcuts import render

from django.views.generic import View

from django.http import HttpResponse

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from r2lab.settings import logger
from r2lab.omfrestview import OmfRestView

from r2lab.isotime import expiration_date

# Create your views here.
class UsersProxy(OmfRestView):

    @method_decorator(csrf_protect)
    def post(self, request, verb):
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
        except Exception as e:
            return self.http_response_from_struct(
                { 'error' : "Failure when running verb {}".format(verb),
                  'message' : e})


    def get_users(self, record):
        """
        retrieve user objects

        xxx In a first implementation, we have not found a means to craft
        a REST URL that allows to pull only one name
        This means that all users are pulled no matter what

        Now, if 'urns' is provided in the input record, it should contain a
        list of urns and only these will be returned

        otherwise all users are returned
        """
        error = self.check_record(record, (), ('urns', ))
        if error:
            return self.http_response_from_struct(error)
        self.init_omf_sfa_proxy()

        post_result = self.loop.run_until_complete(self.co_get_user())
        response, error = self.rain_check(post_result, "get users")
        if error:
            return error
        users = response['resource_response']['resources']
        if 'urns' in record:
            print("input = {} - filtering on {}".format(len(users), record['urns']));
            users = [ user for user in users
                         if user['urn'] in record['urns'] ]
            print("output = {}".format(len(users)));
        return self.http_response_from_struct(users)

    # xxx would be nice to be able to filter right at the API level
    @asyncio.coroutine
    def co_get_user(self):
        url = "users" 
        js = yield from self.omf_sfa_proxy.REST_as_json(url, "GET", None)
        return js
