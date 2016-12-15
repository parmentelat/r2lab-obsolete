from r2lab.settings import testbed_api

if testbed_api == 'plcapi':
   from .plcapi_slices import SlicesProxy
else:
   from .omfrest_slices import SlicesProxy
