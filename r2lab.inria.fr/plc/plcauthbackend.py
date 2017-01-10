#!/usr/bin/env python3

from django.contrib.auth.models import User

##################################################
from rhubarbe.plcapiproxy import PlcApiProxy

from r2lab.settings import plcapi_settings
from r2lab.settings import logger

from plc.plcsfauser import get_r2lab_user

debug = True
config_plcapi_url = plcapi_settings['url']

class PlcAuthBackend:
    """
    Authenticate against the user accounts in r2labapi (a PLCAPI instance)
    """

    def __init__(self, plcapi_url=config_plcapi_url):
        self.plcapi_url = plcapi_url

    # Required for your backend to work properly - unchanged in most scenarios
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    # This is called by the standard Django login procedure
    def authenticate(self, token=None):
        if token is None:
            return

        try:
            email = token['username']
            password = token['password']
            request = token['request']

            if debug:
                logger.info("connecting to plcapi at {}"
                            .format(self.plcapi_url))
            plcapi_proxy = PlcApiProxy(self.plcapi_url,
                                       email=email, password=password)

            # check that email/password
            exists = plcapi_proxy.AuthCheck()
            if exists != 1:
                logger.error("AuthCheck failed, email={}".format(email))
                return None
            persons = plcapi_proxy.GetPersons(
                {'email' : email},
                ['email', 'first_name', 'last_name', 'slice_ids', 'hrn'])
            # should have exactly one
            if len(persons) != 1:
                logger.error("Unexpected : cannot locate person from email")
                return None
            person = persons[0]
            user_details = {
                'email': person['email'],
                'hrn': person['hrn'],
                'firstname': person['first_name'],
                'lastname': person['last_name'],
            }

            # get the slices right at the r2lab portal
            # xxx this is a bit suboptimal, as get_r2lab_user will resend a GetPersons()
            r2lab_user = get_r2lab_user(email)
            if debug:
                logger.info("dbg: r2lab_user = {}".format(r2lab_user))

            if not r2lab_user:
                logger.error("mfbackend.authenticate emergency exit")
                return

            # extend request to save this environment
            # auth and session['expires'] may be of further interest
            # we cannot expose just 'api' because it can't be marshalled in JSON
            # BUT we can expose the 'auth' field
            request.session['r2lab_context'] = {
                'user_details': user_details,
                'accounts': r2lab_user['accounts'],
            }

        except Exception as e:
            logger.exception("ERROR in PLCAPI Auth Backend")
            return None

        try:
            # Check if the user exists in Django's local database
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.info("Creating django user object {}".format(email))
            # Create a user in Django's local database
            # first arg is a name, second an email
            user = User.objects.create_user(
                email, email, 'passworddoesntmatter')

        if 'firstname' in user_details:
            user.first_name = user_details['firstname']
        if 'lastname' in user_details:
            user.last_name = user_details['lastname']

        return user
