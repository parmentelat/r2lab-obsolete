from r2lab.settings import testbed_api

if testbed_api == 'plcapi':
   from .plcapi_leases import LeasesProxy
else:
   from .omfrest_leases import LeasesProxy
