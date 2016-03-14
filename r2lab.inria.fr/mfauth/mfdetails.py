#!/usr/bin/env python3

debug = False

# temporary : search libraries from .. for the micro tester
if __name__ == '__main__':
    import sys
    sys.path.append('..')

# see DEPS.md on how to get these dependencies
from manifold.core.query     import Query
from manifoldapi.manifoldapi import ManifoldAPI

def manifold_details(url, email, password, logger):
    """
    return a tuple with (session, auth, person, slices)
    associated with these credentials at the manifold backend
    
    * session : the session with the manifold API
    * auth : ready-to use auth to talk to the API again
    * user : a flat structure with at least the following keys
      * email, hrn, authority
      * firstname, lastname
    * slices : the list of slice hrns that the person is in

    in case of failure, return tuple with same size with only None's
    """
    failure_result = None, None, None, None
    
    auth = {'AuthMethod': 'password', 'Username': email, 'AuthString': password}
    api = ManifoldAPI(url, auth)
    sessions_result = api.forward(Query.create('local:session').to_dict())
    if debug: print("sessions_result = ", sessions_result)
    sessions = sessions_result.ok_value()
    if not sessions:
        logger.error("GetSession failed: {}".format(sessions_result.error()))
        return failure_result
    session = sessions[0]

    # Change to session authentication
    api.auth = {'AuthMethod': 'session', 'session': session['session']}

    # Get account details
    persons_result = api.forward(Query.get('local:user').to_dict())
    if debug: print("persons_result=", persons_result)
    persons = persons_result.ok_value()
    if not persons:
        logger.error("GetPersons failed: {}".format(persons_result.error()))
        return failure_result
    person = persons[0]
    logger.debug("PERSON : {}".format(person))

    # get related slices
    query = Query.get('myslice:user').filter_by('user_hrn', '==', '$user_hrn').select(['user_hrn', 'slices'])
    mf_result = api.forward(query.to_dict())
    if debug: print("mf_result=", mf_result)
    # xxx - needs more work
    # for now if hrn is not properly filled we want to proceed
    # however this is wrong; it can happen for example
    # when credentials upstream have expired and
    # need to be uploaded again to the manifold end
    # so it would be best to refuse logging in and to provide this kind of hint
    # we don't report login_message properly yet though...
    hrn = "<unknown_hrn>"
    slices = []
    try:
        # xxx use ManifoldResult ?
        # this is a list of dicts that have a 'slices' field
        val_d_s = mf_result['value']
        slices = [ nm for val_d in val_d_s for nm in val_d['slices'] ]
        # in fact there is only one of these dicts because we have specified myslice:user
        hrns = [ val_d['user_hrn'] for val_d in val_d_s ]
        if hrns:
            hrn = hrns[0]
            
    except Exception as e:
        import traceback
        logger.error("mfdetails: Could not retrieve user's slices\n{}"
                     .format(traceback.format_exc()))

    # add hrn in person
    person['hrn'] = hrn
    
    # synthesize our own user structure
    import json
    person_config = json.loads(person['config'])
    user = { 'email' : person['email'],
             'hrn' : hrn,
             'authority' : person_config['authority'],
             'firstname' : person_config['firstname'],
             'lastname' : person_config['lastname'],
             }

    return session, auth, user, slices

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
        tuple = manifold_details(test_manifold_url, email, password, logger)
        end = time.time()
        if tuple[0]:
            print("manifold_details: OK")
            for elem in tuple:
                print("\t{}".format(elem))
        else:
            print("NOPE - manifold_details authenticated KO".format(email, password))
        print("total duration for manifold_details = {}s".format(end-beg))
