import os
import sys
import re
import time
import requests
# Allows snowsecret to be in the user home directory
# Assists in not mistakingly giving away the secret
if os.name == 'nt':
  #Windows!
  sys.path.append(os.environ['USERPROFILE'])
else:
  #assume it's posix!
  sys.path.append(os.environ['HOME'])
import snowsecret

this = sys.modules[__name__]
this.totalcountp = re.compile('X-Total-Count:\s*(\d+)')
this.instance = ''
this.has_proxy = False
this.puppet_user = ''
this.devops_group = ''
this.auth = snowsecret.getValue()
this.headers = {
    'Accept' : 'application/json',
    'Content-Type' : 'application/json',
  }

try:
  import proxysecret
  this.proxies = {
    'https': 'https://%s:%s' % (proxysecret.getIP(), proxysecret.getPort()),
  }
except:
  this.proxies = {}

def getInstance():
  return this.instance

def setInstance(instance):
  this.instance = instance
  getPuppetServiceUser(True)
  getDevOpsGroup(True)

def query(url, verbose=True):
  """ wrapper for pycurl, with settings required to communicate with ServiceNow """
  if verbose:
    print(url)
  resp = requests.get(url, proxies=this.proxies, headers=this.headers, verify=False, auth=this.auth)
  return (int(resp.headers['X-Total-Count']), resp.json())

def update(instance, table, sysid, data):
  """update arbitrary data of object with sys_id sysid"""
  url = 'https://%s/api/now/table/%s/%s' % (instance, table, sysid)
  resp = requests.update(url, proxies=this.proxies, headers=this.headers, verify=False, auth=this.auth)
  return resp.text

def setDataByJson(instance, table, data):
  """insert data into table table of instance instance"""
  url = 'https://%s/api/now/table/%s/%s' % (instance, table, sysid)
  resp = requests.post(url, proxies=this.proxies, headers=this.headers, verify=False, auth=this.auth)
  return resp.json

def getTableResults(instance, table, fieldsa=[], func=None, encodedqs=''):
  """returns a generator of data in table table of instance instance
     where fieldsa is the list of fields to limit retrieval
     func is a custom filter function on the retrieved data
     encodedqs is the query string as per ServiceNow table API"""
  offset = 0
  count = 0
  fieldstr = ','.join(fieldsa)
  if fieldstr:
    fieldstr = 'sysparm_fields=%s&' % fieldstr
  urif = 'https://%(instance)s/api/now/table/%(table)s?%(fieldstr)ssysparm_offset=%%(offset)d&sysparm_limit=10000&%%(encodedqs)s' % locals()
  myfunc = lambda x: x
  if callable(func):
    myfunc = func
  total, qoutput = query(urif % locals())
  data = qoutput
  print(data)
  while (total > count):
    for ele in data['result']:
      count += 1
      if myfunc(ele):
        yield ele
    offset += 10000
    if (total > count):
      data = query(urif % locals())[1]

def getDevOpsGroup(new=False):
  """returns the sys_id of the DevOps group"""
  if new:
    qs = 'name=DevOps'
    group = next(getTableResults(instance, 'sys_user_group', ['sys_id'], None, qs))
    this.devops_group = str(group['sys_id'])
  return this.devops_group

def getPuppetServiceUser(new=False):
  """return the sys_id of the puppet sys_user account"""
  if new:
    qs = 'user_name=puppet'
    user = next(getTableResults(instance, 'sys_user', ['sys_id'], None, qs))
    this.puppet_user = str(user['sys_id'])
  return this.puppet_user

__all__ = map(lambda k,v: k, filter(lambda k,v: callable(v), globals().items()))

