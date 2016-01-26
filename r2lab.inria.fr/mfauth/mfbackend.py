#!/usr/bin/env python3

from django.contrib.auth.models import User

##################################################
from manifoldapi.manifoldapi    import ManifoldException
from manifold.core.query        import Query

from .mfsession import get_session

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

    # Create an authentication method
#    def authenticate(self, email, password):
#        return get_session(self.manifold_url, email, password)

    # This is called by the standard Django login procedure
    def authenticate(self, token=None):
        print("AUTHENTICATE!")
        if not token:
            return None
        
        person = {}

        try:
            email = token['username']
#            username = email.split('@')[-1]
            password = token['password']
            request = token['request']

            session = get_session(self.manifold_url, email, password, logger)
            if not session:
                return None
            logger.debug("SESSION : {}".format(session.keys()))
            
            # Change to session authentication
            api.auth = {'AuthMethod': 'session', 'session': session['session']}
            self.api = api

            # Get account details
            # the new API would expect Get('local:user') instead
            persons_result = api.forward(Query.get('local:user').to_dict())
            persons = persons_result.ok_value()
            if not persons:
                logger.error("GetPersons failed: {}".format(persons_result.error()))
                return None
            person = persons[0]
            logger.debug("PERSON : {}".format(person))
            
            request.session['manifold'] = {'auth': api.auth, 'person': person, 'expires': session['expires']}

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
            # Create a user in Django's local database
            user = User.objects.create_user(username, email, 'passworddoesntmatter')
            user.email = person['email']

        if 'firstname' in person:
            user.first_name = person['firstname']
        if 'lastname' in person:
            user.last_name = person['lastname']

#        request.session['user'] = {
#            'email' : user.email,
#            'firstname' : user.first_name,
#            'lastname' : user.last_name,
#        }
        return user

