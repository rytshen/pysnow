from pysnow.base import *
import sys
this = sys.modules[__name__]

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
  data.pop('instance', None)
  return setDataByJson(instance, 'incident', data)

__all__ = [
  'optForPuppet',
]

