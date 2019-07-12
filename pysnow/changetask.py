import sys
from pysnow.base import *
this = sys.modules[__name__]

def addAffectedCIForChange(instance, task, ci_item):
  """insert CI ci_item (sys_id as key) into a change task (sys_id as key) as an affected CI
     NOTE: this works even if the task is no longer open"""
  data = vars()
  data.pop('instance', None)
  setDataByJson(instance, 'task_ci', data)

def getPendingChangeRequestByCI(instance, ci):
  """return the list of pending change requests with ci ci (sys_id as key)"""
  qs = 'cmdb_ci=%s' % ci
  myfunc = lambda x: int(x['state']) < 0
  return map(lambda x: str(x['sys_id']), getTableResults(instance, 'change_request', ['sys_id','state'], myfunc, qs))

def getOpenChangeRequests(instance, query_dict):
  """return the list of sys_ids of the open change requests that match all the field/values in query_dict
     see getOpenChangeRequestsByCI as an example"""
  query_dict['phase_state'] = 'open'
  import urllib
  qs = urllib.parse.urlencode(query_dict)
  return getTableResults(instance, 'change_request', ['sys_id','number'], None, qs)

def getOpenChangeRequestsByCI(instance, ci_sys_id):
  """return the list of sys_ids of the open change requests that has configuration item with sys_id ci_sys_id"""
  q = { 'cmdb_ci': ci_sys_id }
  return getOpenChangeRequest(instance, q)

def getStartedImplementTasksForGroup(instance, change_request, group=''):
  """return the generator for open tasks with the short_description Implement, with past due expected start time and
     associated with the change request of sys_id change_request"""
  import datetime
  import urllib
  n = datetime.datetime.utcnow()
  q = { 'state':'1',
        'parent':change_request,
        'short_description':'Implement',
      }
  if group != '':
    q['assignment_group'] = group

  def test(data):
    return n.strptime(data['expected_start'], "%Y-%m-%d %H:%M:%S") <= n

  return getTableResults(instance, 'change_task', ['sys_id', 'number', 'expected_start'], test, urllib.urlencode(q))

def getStartedImplementTasksForDevops(instance, change_request):
  return getStartedImplementTasksForGroup(instance, change_request, getDevOpsGroup())

def getOpenImplementTasks(instance, change_request, func=None):
  """return the generator for open tasks with the short_description Implement
     associated with the change request of sys_id change_request"""
  qs = 'state=1&parent=%s&short_description=Implement' % change_request
  return getTableResults(instance, 'change_task', ['sys_id', 'number'], func, qs)

def getOpenImplementTaskNumber(instance, change_request):
  """return the open Implement task number associated with change request (sys_id)
      throws exception ValueError if no Implement task is open"""
  try:
    task = next(getOpenImplementTasks(instance, change_request))
    return task['number']
  except:
    raise ValueError

def updateTaskBySysId(instance, sys_id, state):
  """update a task with the sys_id with state state"""
  data = {
   'assignment_group': getDevOpsGroup(),
   'assigned_to'     : getPuppetServiceUser(),
   'state'           : state,
  }
  return patch(instance, 'change_task', sys_id, data)

def addWorkNotes(instance, sys_id, notes):
  """add work notes to change_task sys_id"""
  data = { 'work_notes' : notes }
  return patch(instance, 'change_task', sys_id, data) 

def createTaskByJsonData(instance, data):
  """create task with fields specified in data (json object)"""
  setDataByJson(instance, 'task', data)

def createTaskForChange(instance, short_description, description, assignment_group, change_request):
  """create a task in change request change_request"""
  data = vars()
  data.pop('instance', None)
  data['sys_class_name'] = 'change_task'
  createTaskByJsonData(instance, data)

def createVTBTask(instance, short_description, description, assignment_group):
  """create task for visual task boards"""
  data = vars()
  data.pop('instance', None)
  data['sys_class_name'] = 'vtb_task'
  createTaskByJsonData(instance, data)

this.TASK_COMPLETE = 3
this.TASK_START = 2
__all__ = [
  'addWorkNotes',
  'addAffectedCIForChange',
  'getPendingChangeRequestByCI',
  'getOpenChangeRequests',
  'getOpenChangeRequestsByCI',
  'getStartedImplementTasksForGroup',
  'getStartedImplementTasksForDevops',
  'getOpenImplementTasks',
  'getOpenImplementTaskNumber',
  'updateTaskBySysId',
  'createTaskByJsonData',
  'createTaskForChange',
  'createVTBTask',
  'TASK_COMPLETE',
  'TASK_START'
]
