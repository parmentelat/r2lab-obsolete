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
    return a tuple with (session, auth, person, slices)
    associated with these credentials at the manifold backend
    
    * session : the session with the manifold API
    * auth : ready-to use auth to talk to the API again
    * person : the manifold object as-is - looks like this
	{'status': 2, 'config': '{"firstname": "Thierry", 
                                  "lastname": "Parmentelat", 
                                  "authority": "onelab.inria"}',
         'user_id': 55, 'email': 'thierry.parmentelat@inria.fr', 'password': '<>'}
    * slices : the list of slice hrns that the person is in

    in case of failure, return tuple with same size with only None's
    """
    failure_result = None, None, None, None
    
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

    # get related slices
    query = Query.get('myslice:user').filter_by('user_hrn', '==', '$user_hrn').select(['user_hrn', 'slices'])
    mf_result = api.forward(query.to_dict())
    try:
        # xxx use ManifoldResult ?
        # this is a list of dicts that have s 'slices' field
        nm_d_s = mf_result['value']
        slices = [ nm for nm_d in nm_d_s for nm in nm_d['slices'] ]
    except Exception as e:
        import traceback
        logger.error("mfdetails: Could not retrieve user's slices\n{}"
                     .format(traceback.format_exc()))
        slices = []

    return session, auth, person, slices

####################
if __name__ == '__main__':

    test_manifold_url = "https://portal.onelab.eu:7080/"

    default_tests = [
        # should succeed
        ( 'demo', 'demo'),
        # should fail
        ( 'demo', 'not-the-password'),
    ]

    # with an empty argv, we use the tests above
    # but you can also specify mail and password on the command line
    import sys
    args = sys.argv[1:]
    if not args:
        tests = default_tests
    elif len(args) % 2 != 0:
        print("need an even number of args (email / passwd)")
        exit(1)
    else:
        def chunks(l, n):
            """Yield successive n-sized chunks from l."""
            for i in range(0, len(l), n):
                yield l[i:i+n]
        tests = chunks(args, 2)
    

    import logging
    logger = logging.getLogger('session')
    for email, password in tests:
        print(10*'=', "testing {} / {}".format(email, password))
        import time
        beg = time.time()
        tuple = get_details(test_manifold_url, email, password, logger)
        end = time.time()
        if tuple[0]:
            print("get_details: OK")
            for elem in tuple:
                print("\t{}".format(elem))
        else:
            print("NOPE - get_details authenticated KO".format(email, password))
        print("total duration for get_details = {}s".format(end-beg))
