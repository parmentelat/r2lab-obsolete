#!/usr/bin/env python3

# temporary : search libraries from .. for the micro tester
if __name__ == '__main__':
    import sys
    sys.path.append('..')

# see DEPS.md on how to get these dependencies
from manifold.core.query     import Query
from manifoldapi.manifoldapi import ManifoldAPI

def get_details(url, email, password, logger):
    """
    return a tuple with (session, person, api)
    associated with these credentials at the manifold backend
    
    in case of failure, return tuple with same size with only None's
    """
    failure_result = None, None, None
    
    auth = {'AuthMethod': 'password', 'Username': email, 'AuthString': password}
    api = ManifoldAPI(url, auth)
    sessions_result = api.forward(Query.create('local:session').to_dict())
    sessions = sessions_result.ok_value()
    if not sessions:
        logger.error("GetSession failed: {}".format(sessions_result.error()))
        return failure_result
    session = sessions[0]

    # Change to session authentication
    api.auth = {'AuthMethod': 'session', 'session': session['session']}

    # Get account details
    persons_result = api.forward(Query.get('local:user').to_dict())
    persons = persons_result.ok_value()
    if not persons:
        logger.error("GetPersons failed: {}".format(persons_result.error()))
        return failure_result
    person = persons[0]
    logger.debug("PERSON : {}".format(person))
    return session, person, api

####################
if __name__ == '__main__':

    test_manifold_url = "https://portal.onelab.eu:7080/"

    tests = [
        # should succeed
        ( 'demo', 'demo'),
        # should fail
        ( 'demo', 'not-the-password'),
    ]

    import logging
    logger = logging.getLogger('session')
    for email, password in tests:
        session, person, api = get_details(test_manifold_url, email, password, logger)
        if session:
            print("get_session: OK with {} / {} : returned\nsession\t{}\nperson\t{}\napi\t{}\n".
                  format(email, password, session, person, api))
            api_ok = api
        else:
            print("get_session: NOPE with {} / {} : authenticated KO".format(email, password))
