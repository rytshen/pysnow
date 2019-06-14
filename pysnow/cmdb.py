import sys
import re
from pysnow.base import *

this = sys.modules[__name__]
this.dppoolp = re.compile('ThinProvisioningPool:.*\.(\d+)\.(\d+)')
this.reltypes = {}
this.fns = { True: lambda p,c: (p,c), False: lambda p,c: (c,p) }

def setRelationship(instance, parent, type_str_val, child, verbose=False):
  if instance != getInstance():
    initRelationshipCache(instance)
    setInstance(instance)

  data = {
    'parent': parent,
    'type': this.reltype[type_str_val],
    'child': child
  }
  if verbose:
    print(setDataByJson(instance, 'cmdb_rel_ci', data))
  else:
    setDataByJson(instance, 'cmdb_rel_ci', data)
  
def getFCDiskModels(instance):
  """return all SAN team FC disk types"""
  result = {}
  p = re.compile('.*(USP_V|VSP|OPEN-V|FS1-2|3PAR|2145 IBM|IBM 2145|IBM 2076).*')
  for i in getTableResults(instance, 'cmdb_model',['display_name','sys_id']):
    m = p.match(i['display_name'])
    if m:
      result[i['sys_id']] = i['display_name']
  return result

def relResultHelper(i, result, parentKey=False):
  """helper function to manage CMDB CI relationships"""
  try:
    t = i['type']['value']
    k, av = this.fns[parentKey](i['parent']['value'],i['child']['value'])
    try:
      td = result[t]
    except:
      result[t] = {}
      td = result[t]
    try:
      kd = td[k]
    except:
      td[k] = []
      kd = td[k]
    kd.append(av)
  except KeyError:
    pass
  except TypeError:
    pass

def initRelationshipCache(instance):
  """initialize data for library related to relationship types"""
  this.reltypes = dict((e['name'], e['sys_id']) for e in getTableResults(instance, 'cmdb_rel_type',['name','sys_id']))

def getClusters(instance):
  """get the sys_ids of VMWare clusters"""
  if instance != getInstance():
    initRelationshipCache(instance)
    setInstance(instance)
  vccluster = set(map(lambda e: e['sys_id'], getTableResults(instance, 'cmdb_ci_vcenter_cluster', ['sys_id'])))
  result = {}
  typesysid = this.reltypes[u'Members::Member of']
  qs = 'type=%s' % str(typesysid)
  fields = ['parent','child','type']
  for i in getTableResults(instance, 'cmdb_rel_ci', fields, None, qs):
    relResultHelper(i, result, True)
  #for k,v in result[typesysid].items():
  #  print k,"len",len(v)
  return dict(filter(lambda items: items[0] in vccluster, result[typesysid].items()))

def getRelationships(instance, relstr='', func=None):
  """get the relationships in CMDB"""
  if instance != getInstance():
    initRelationshipCache(instance)
    setInstance(instance)
  qs = 'type=%s' % str(this.reltypes[relstr])
  return getTableResults(instance, 'cmdb_rel_ci', [], func, qs) 

def getPuppetRelationships(instance, relstr=''):
  """get CMDB relationships that were populated by puppet service account"""
  if instance != getInstance():
    initRelationshipCache(instance)
    setInstance(instance)
  qs = 'sys_created_by=puppet'
  fields = ['parent','child','type']
  result = {}
  it = getTableResults(instance, 'cmdb_rel_ci', fields, None, qs) 
  for i in it:
    relResultHelper(i, result)
  if relstr:
    try:
      typesysid = this.reltypes[relstr]
      return result[typesysid]
    except:
      pass
  return result

def getComputerFCPorts(instance):
  """gets all the WWPN of computer FC ports
     returns a hash where:
       key is the sys_id of the computer
       value is a hash where:
         key is the sys_id of the FC port 
         value is the canonlib-formated WWPN""" 
  if instance != getInstance():
    initRelationshipCache(instance)
    setInstance(instance)
  result = {}
  from canonlib import getCanonicalHexFromWWNStr
  qs = 'sysparm_query=provided_byISNOTEMPTY'
  it = getTableResults(instance, 'cmdb_ci_fc_port', ['computer','wwpn','sys_id'])
  for i in it:
    canonwwpn = getCanonicalHexFromWWNStr(i['wwpn'])
    try:
      csysid = i['computer']['value']
      try:
        result[csysid][i['sys_id']] = canonwwpn
      except KeyError:
        result[csysid] = { i['sys_id'] : canonwwpn }
    except:
      pass
  return result

def purgeOldPuppetRelationships(instance, datetimet):
  """deletes all relationships created by puppet service account
     that is older than datatimet"""
  if instance != getInstance():
    initRelationshipCache(instance)
    setInstance(instance)
  s = "sys_created_by=puppet^sys_created_on<javascript:gs.dateGenerate('%s','%s')" % datetimet
  import urllib
  qs = 'sysparm_query=%s' % urllib.quote(s, "()'")
  fields = ['sys_id','sys_created_on']
  result = {}
  it = getTableResults(instance, 'cmdb_rel_ci', fields, None, qs)
  for i in it:
    deleteRelationship(instance, i['sys_id'])

def getRelationshipTypes(instance):
  """returns all existing relationship types in CMDB
     as hash with key as the readable string of the relationship
     and the value is the sys_id"""
  alltypes = {}
  for i in getTableResults(instance, 'cmdb_rel_type',['name','sys_id']):
    alltypes[i['name']] = i['sys_id']
  return alltypes

def getStorageSysIds(instance):
  """returns a hash that is used to lookup the sys_id of storage
     with either search key of name or serial_number"""
  sysmap = {}
  for i in getTableResults(instance, 'cmdb_ci_storage_server',['name','sys_id','serial_number']):
    sysmap[i['name']] = i['sys_id']
    sysmap[i['serial_number']] = i['sys_id']
  return sysmap

def getDPPoolSysIds(instance):
  """returns all the hitachi DP Pool sys_ids"""
  result = {}
  for i in getTableResults(instance, 'cmdb_ci_storage_pool',['pool_id','sys_id']):
    m = this.dppoolp.match(i['pool_id'])
    if m:
      serial = m.group(1)
      poolid = int(m.group(2))
      if serial in result:
        result[serial][poolid] = i['sys_id']
      else:
        result[serial] = { poolid : i['sys_id'] }
  return result

def getIPComputerSysIdDict(instance):
  """returns a hashmap with primary keys of ip addresses
     to get the sys_id of the computer with that ip address"""
  computerset = set([])
  def setComputer(e):
    computerset.add(e['sys_id'])
    if ('ip_address' in e):
      return (e['ip_address'], e['sys_id'])
    return (None, None)

  def isComp(e):
    try:
      if isinstance(e['cmdb_ci'], dict):
        return e['cmdb_ci']['value'] in computerset
      else:
        return e['cmdb_ci'] in computerset
    except:
      return False

  result = dict(map(setComputer, getTableResults(instance, 'cmdb_ci_computer',['sys_id','ip_address'], None, 'install_status=1')))
  nicfields = ['sys_id','cmdb_ci']
  niciter = getTableResults(instance, 'cmdb_ci_network_adapter', nicfields, isComp)
  nic2computer = dict(map(lambda e: (e['sys_id'], e['cmdb_ci']['value']), niciter))
  count = 0
  for e in getTableResults(instance, 'cmdb_ci_ip_address',['nic','ip_address']):
    if ('nic' in e) and (e['nic']['value'] in nic2computer):
      count += 1
      result[e['ip_address']] = nic2computer[e['nic']['value']]

  return result

__all__ = [
  'setRelationship',
  'getFCDiskModels',
  'initRelationshipCache',
  'getClusters',
  'getPuppetRelationships',
  'getComputerFCPorts',
  'purgeOldPuppetRelationships',
  'getRelationshipTypes',
  'getStorageSysIds',
  'getDPPoolSysIds',
  'getIPComputerSysIdDict'
]
