#!/usr/bin/env python3

# temporary : search libraries from .. for the micro tester
if __name__ == '__main__':
    import sys
    sys.path.append('..')

# see DEPS.md on how to get these dependencies
from manifold.core.query     import Query
from manifoldapi.manifoldapi import ManifoldAPI

def get_session(url, email, password, logger):
    #    print("validating {} -- {}".format(email, password))
    auth = {'AuthMethod': 'password', 'Username': email, 'AuthString': password}
    api = ManifoldAPI(url, auth)
    sessions_result = api.forward(Query.create('local:session').to_dict())
    sessions = sessions_result.ok_value()
    if not sessions:
        logger.error("GetSession failed: {}".format(sessions_result.error()))
        return None
    return sessions[0]

####################
if __name__ == '__main__':

    test_manifold_url = "https://portal.onelab.eu:7080/"

    tests = [
        # should succeed
        ( 'demo', 'demo'),
        # should fail
        ( 'demo', 'not-the-password'),
    ]

    for email, password in tests:
        if get_session(test_manifold_url, email, password):
            print("get_session: {} / {} : authenticated OK".format(email, password))
        else:
            print("get_session: NOPE with {} / {} : authenticated KO".format(email, password))

