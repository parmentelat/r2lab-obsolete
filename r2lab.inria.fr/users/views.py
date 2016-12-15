from r2lab.settings import testbed_api

if testbed_api == 'plcapi':
   from .plcapi_users import UsersProxy
else:
   from .omfrest_users import UsersProxy

