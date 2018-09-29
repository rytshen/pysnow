snowlib contains many utility functions that use the ServiceNow table API.

To get started, create a snowsecret.py in the user home directory that contains
the following:
```Python
def getValue():
  return '<username>:<password>'
```

where the credentials are of an account that has rights to ServiceNow table APIs
required to get the data from ServiceNow.

The caveat is that if access to ServiceNow requires proxy credentials, also
require a proxysecret.py with the following:
```Python
def getProxy():
  return '<The proxy url>'

def getValue():
  return '<username>:<password>'
```

Where the proxy is assumed to use NTLM authentication, and the same credentials
will be used by ServiceNow (instead of the value `snowsecret.getValue()`)