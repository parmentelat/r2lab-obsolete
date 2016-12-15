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
from omf.omfrestview import OmfRestView

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

        Now, if 'urn' is provided in the input record, it should contain a
        URN and only this one will be returned

        otherwise all users are returned
        """
        error = self.check_record(record, (), ('urn', ))
        if error:
            return self.http_response_from_struct(error)
        self.init_omf_sfa_proxy()

        if 'urn' in record:
            post_result = self.loop.run_until_complete(self.co_get_user(record['urn']))
            response, error = self.rain_check(post_result, "get user")
        else:
            post_result = self.loop.run_until_complete(self.co_get_users())
            response, error = self.rain_check(post_result, "get users")
        if error:
            return error
        users = response['resource_response']['resources']
        return self.http_response_from_struct(users)

    @asyncio.coroutine
    def co_get_users(self):
        js = yield from self.omf_sfa_proxy.REST_as_json("users", "GET", None)
        return js

    @asyncio.coroutine
    def co_get_user(self, urn):
        encoded_urn = urn.replace("+", "%2b")
        path = "users?urn={}".format(encoded_urn)
        js = yield from self.omf_sfa_proxy.REST_as_json(path, "GET", None)
        return js
