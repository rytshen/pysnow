from pysnow.base import *, setDataByJson
import sys
this = sys.modules[__name__]

def puppetNotReporting(instance, ci_item, behalf, date):
  """Create an incident for Puppet not running on ci_item"""

  if getInstance() != instance:
    setInstance(instance)

  try:
    query_dict = {
      "cmdb_ci": ci_item,
      "short_description": "puppet agent not running since %s" % date,
    }
    import urllib
    qs = urllib.parse.urlencode(query_dict)
    existing = next(getTableResults(instance, 'incident', encodedqs=qs))
    return existing
  except:
    data = {
      "description":"Puppet agent is not running",
      "short_description": "puppet agent not running since %s" % date,
      "subcategory": "Operating System",
      "category": "Software",
      "caller_id":str(getPuppetServiceUser()),
      "cmdb_ci":ci_item,
      "on_behalf_of":behalf,
      "assignment_group":"a3448ed2dbcf3640948f71dabf96196d",
      "location":"42b67d88db073e00948f71dabf961925",
      "contact_type":"email",
    }
    return setDataByJson(instance, 'incident', data)

def optForPuppet(instance, ci_item, behalf):
  """Create an incident to expand opt space required for Puppet to run for ci_item"""

  if getInstance() != instance:
    setInstance(instance)

  data = {
    "description":"Please expand /opt space. Puppet needs 1G of free space.",
    "short_description": "for puppet -- /opt disk space needs expansion",
    "subcategory": "Operating System",
    "category": "Software",
    "caller_id":str(getPuppetServiceUser()),
    "cmdb_ci":ci_item,
    "on_behalf_of":behalf,
    "assignment_group":"a3448ed2dbcf3640948f71dabf96196d",
    "location":"42b67d88db073e00948f71dabf961925",
    "contact_type":"email",
  }
  return setDataByJson(instance, 'incident', data)

__all__ = [
  'optForPuppet',
  'puppetNotReporting',
]

