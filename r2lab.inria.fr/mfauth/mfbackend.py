#!/usr/bin/env python3

from django.contrib.auth.models import User

##################################################
from manifoldapi.manifoldapi    import ManifoldException
from manifold.core.query        import Query

from .mfsession import get_details

from r2lab.settings import manifold_url as config_manifold_url
from r2lab.settings import logger

#from myslice.settings import config, logger, DEBUG

class ManifoldBackend:
    """
    Authenticate against the onelab portal user accounts
    """
    def __init__(self, manifold_url=config_manifold_url):
        self.manifold_url = manifold_url

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

            session, person, api = get_details(self.manifold_url, email, password, logger)
            if session is None or person is None:
                return None
            logger.debug("SESSION : {}".format(session.keys()))
            
            # extend request to save this environment
            # api.auth and session['expires'] may be of further interest
            request.session['r2lab_context'] = {'session' : session,
                                                'auth': api.auth,
                                                'person': person,
                                                'manifold_url' : self.manifold_url,
            }

        except ManifoldException as e:
            logger.error("ManifoldException in Auth Backend: {}".format(e.manifold_result))
        except Exception as e:
            logger.error("Unexpected exception in Manifold Auth Backend: {}".format(e))
            import traceback
            logger.error(traceback.format_exc())
            return None

        try:
            # Check if the user exists in Django's local database
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.debug("Creating django user object")
            # Create a user in Django's local database
            # first arg is a name, second an email
            user = User.objects.create_user(email, email, 'passworddoesntmatter')

        if 'firstname' in person:
            user.first_name = person['firstname']
        if 'lastname' in person:
            user.last_name = person['lastname']

        request.session['r2lab_context'].update({'user' : { 'email' : user.email,
                                                            'firstname' : user.first_name,
                                                            'lastname' : user.last_name,
                                                        }})
        return user

