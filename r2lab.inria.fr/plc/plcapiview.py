import time
import calendar
import json
import asyncio

from django.http import HttpResponse

from r2lab.testbedapiview import TestbedApiView

# essentially, this describes the OMF REST API endpoint details
from r2lab.settings import plcapi_settings, logger

### the standard way to use rhubarbe is to have it installed separately
try:
    from rhubarbe.plcapiproxy import PlcApiProxy
# in a standalone / devel environment however, just create a symlink
except:
    from .plcapiproxy import PlcApiProxy

debug = False
debug = True

def init_plcapi_proxy():
    # we use this location on r2lab.inria.fr which is readable by apache
    found = False
    for credentials in plcapi_settings['credentials']:
        try:
            with open(credentials) as cfile:
                email, password = cfile.read().split()
                found = True
                break
        except FileNotFoundError as e:
            pass
    if not found:
        logger.error("Cannot find credentials to use for plcapi")
        for credentials in plcapi_settings['credentials']:
            logger.error("have tried in {}".format(credentials))

    return PlcApiProxy(plcapi_settings['url'],
                       email=email,
                       password=password,
                       debug=debug,
    )

class PlcApiView(TestbedApiView):

    # the code in rhubarbe does not yet do this asynchroneously
    # we want to leverage the code from rhubarbe that does all this
    # but asynchroneously
    # we need to create a loop object for each hit on this URL
    # asyncio does create a loop object (get_event_loop())
    # but this is attached to main thread, it's not usable in this context
    # xxx we might need to do some cleanup on loops at some point 
    def init_plcapi_proxy(self):
        if hasattr(self, 'plcapi_proxy'):
            return self.plcapi_proxy
        self.plcapi_proxy = init_plcapi_proxy()
        self._unique_component_name = None
        return self.plcapi_proxy

    def unique_component_name(self):
        if not self._unique_component_name:
            seed = plcapi_settings['nodename_match']
            # search all nodes that have the seed in their hostname
            nodes = self.plcapi_proxy.GetNodes(
                { 'hostname' : '*{}*'.format(seed)}
            )
            # take first match no matter what
            # should be only one anyways
            self._unique_component_name = nodes[0]['hostname']
        return self._unique_component_name
            
    # tmp for migration
    def ensure_plc_slicename(self, slicename):
        """
        if slicename does not come with a '_' then it needs one
        """
        if '_' not in slicename:
            ol, site, *rest = slicename.split('.')
            return '{}_{}'.format(site, '.'.join(rest))
        else:
            return slicename

    ##########
    # UI creates timestamps like 2017-02-20T09:00:00Z
    # and plcapi accepts timestamps like 2017-02-20 09:00:00
    def ui_ts_to_plc_ts(self, ui_timestamp):
        return ui_timestamp.replace('T', ' ').replace('Z', '').replace('.000', '')

    @staticmethod
    def epoch_to_ui_ts(epoch):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))

    def ui_ts_to_epoch(self, ui_timestamp):
        if isinstance(ui_timestamp, int):
            return ui_timestamp
        elif isinstance(ui_timestamp, float):
            return int(ui_timestamp)
        return calendar.timegm(
            time.strptime(ui_timestamp, "%Y-%m-%dT%H:%M:%SZ"))

