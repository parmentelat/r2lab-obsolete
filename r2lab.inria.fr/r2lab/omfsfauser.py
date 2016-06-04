import asyncio
import json

# essentially, this describes the OMF REST API endpoint details
from r2lab.settings import omfrest_settings, logger

### the standard way to use rhubarbe is to have it installed separately
try:
    from rhubarbe.omfsfaproxy import OmfSfaProxy
# in a standalone / devel environment however, just create a symlink
except:
    from .omfsfaproxy import OmfSfaProxy

@asyncio.coroutine
def co_get_user(urn, loop):
    omf_sfa_proxy \
        = OmfSfaProxy(omfrest_settings['hostname'],
                      omfrest_settings['port'],
                      omfrest_settings['root_pem'], None,
                      omfrest_settings['nodename'],
                      loop=loop)
    encoded_urn = urn.replace("+", "%2b")
    path = "users?urn={}".format(encoded_urn)
    post_result = yield from omf_sfa_proxy.REST_as_json(path, "GET", None)
    try:
        parsed = json.loads(post_result)
        if 'resource_response' in parsed:
            return parsed['resource_response']['resources'][0]
    except:
        logger.exception("fetching user accounts at R2lab")
        return None

def get_r2lab_user(urn):
    """
    This function retrieves at the r2lab omf-sfa db the list of slices
    that a user is attached to, together with all the attached details 
    """

    loop = asyncio.new_event_loop()
    return loop.run_until_complete(co_get_user(urn, loop))
