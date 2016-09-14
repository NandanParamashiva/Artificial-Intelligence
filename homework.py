#!/usr/bin/env python

from sys import exit
from collections import deque

_DEBUG_ENABLE = True
OFFSETLIVETRAFFIC = 4
ROOTNODEID = -100
ALGOS = ('BFS', 'DFS', 'UCS', 'A*')

def Debug_print(msg):
  """ Method to print the debug messages """
  global _DEBUG_ENABLE
  if _DEBUG_ENABLE is True:
    print 'DEBUG:'+ msg


class _Node(object):
  """ Stores the paramas """
  def __init__(self):
    # NOTE: NodeIds are always >= 1
    self.nodeId = -1
    self.state = None
    self.g = -1 #cost
    self.parentNodeId = -1

  def SetNodeValues(self, nodeId, state, g, parentNodeId):
    self.nodeId = nodeId
    self.state = state
    self.g = g
    self.parentNodeId = parentNodeId

  def GetNodeId(self):
      return self.nodeId

  def GetState(self):
      return self.state

  def GetG(self):
      return self.g

  def GetParentNodeID(self):
      return self.parentNodeId


class _InputParams(object):
  """ Maintains the parameters specified in input.txt """
  def __init__(self):
    self.algo = None
    self.start_state = None
    self.goal_state = None
    self.num_live_trafficlines = 0
    self.dict_live_traffic = {}
    self.num_sunday_trafficlines = 0
    self.dict_sunday_traffic = {}

  def SetAlgo(self, algo):
    self.algo = algo

  def SetStartState(self, start_state):
    self.start_state = start_state

  def SetGoalState(self, goal_state):
    self.goal_state = goal_state

  def SetNumLiveTrafficLines(self, num_live_trafficlines):
    self.num_live_trafficlines = num_live_trafficlines

  def SetSundayTrafficLines(self, num_sunday_trafficlines):
    self.num_sunday_trafficlines = num_sunday_trafficlines

  def GetAlgo(self):
    return self.algo

  def GetStartState(self):
    return self.start_state

  def GetGoalState(self):
    return self.goal_state

  def GetNumLiveTrafficLines(self):
    return self.num_live_trafficlines

  def GetSundayTrafficLines(self):
    return self.num_sunday_trafficlines

  def DisplayInputParams(self):
    print'**************_InputParams**************'
    print'%-25s'%'algo',':','%s'%self.algo
    print'%-25s'%'start_state',':','%s'%self.start_state
    print'%-25s'%'goal_state',':','%s'%self.goal_state
    print'%-25s'%'num_live_trafficlines',':','%s'%self.num_live_trafficlines
    print'%-25s'%'dict_live_traffic'
    print'-----------------'
    for src in self.dict_live_traffic:
      print src,':',self.dict_live_traffic[src]
    print'%-25s'%'num_sunday_trafficlines',':','%s'%self.num_sunday_trafficlines
    print'%-25s'%'dict_sunday_traffic'
    print'-------------------'
    for src in self.dict_sunday_traffic:
      print src,':',self.dict_sunday_traffic[src]
    print'******* END of _InputParams**************\n'

  def BuildDictLiveTraffic(self, lines):
    """ Builds the dictonary/map to store the Live Traffic 
        Note:
        1. Key i.e Parent --> Value i.e List of (child,cost).
        2. The List is stored in the order of occurence in input.txt 
        Example:
          From the spec example1:
          {
           A:[(B,5),(C,3)],
           B:[(D,1)]      ,
           C:[(D,2)]      
          }
    """
    end_offset_liveTraffic = OFFSETLIVETRAFFIC + self.GetNumLiveTrafficLines()
    for linenum in range(OFFSETLIVETRAFFIC , end_offset_liveTraffic):
      line = lines[linenum]
      temp = line.split()
      if len(temp) is not 3:
        Debug_print('Error, Live traffic line in input.txt should have 3 params')
        exit()
      src = temp[0]
      dst = temp[1]
      pathcost = int(temp[2])
      if self.GetAlgo() == 'BFS' or self.GetAlgo() == 'DFS':
        pathcost = 1
      if src not in self.dict_live_traffic:
        self.dict_live_traffic[src] = []
      self.dict_live_traffic[src].append((dst,pathcost))

  def BuildDictSundayTraffic(self, lines):
    """ Builds the dictonary/map to store the Sunday Traffic 
        Note:
        1. Key i.e Source --> Value i.e Cost.
        Example:
          From the spec example1:
          {
           A:4,
           B:1,
           C:1,
           D:0      
          }
    """
    start_offset_sundayTraffic = OFFSETLIVETRAFFIC + self.GetNumLiveTrafficLines() + 1
    end_offset_sundayTraffic = start_offset_sundayTraffic + self.GetSundayTrafficLines()
    for linenum in range(start_offset_sundayTraffic, end_offset_sundayTraffic):
      line = lines[linenum]
      temp = line.split()
      if len(temp) is not 2:
        Debug_print('Error, Sunday traffic line in input.txt should have 2 params')
        exit()
      src = temp[0]
      try:
        cost = int(temp[1])
      except ValueError:
        Debug_print('Error, Parsing input.txt')
        exit()
      if src not in self.dict_sunday_traffic:
        self.dict_sunday_traffic[src] = cost


#_input_params = _InputParams()

def ParseInputFile(_input_params):
  """ Parses the input file """
  fd_input = open('input.txt', 'r')
  lines = fd_input.read().split('\n')
  #print(lines)

  algo = lines[0]
  if algo not in ALGOS:
    Debug_print('Error, Parsing algo in input.txt')
    fd_input.close()
    exit()
  _input_params.SetAlgo(algo)

  start_state = lines[1]
  _input_params.SetStartState(start_state)

  goal_state = lines[2]
  _input_params.SetGoalState(goal_state)

  try: 
    num_live_trafficlines = int(lines[3])
    _input_params.SetNumLiveTrafficLines(num_live_trafficlines)
  except ValueError:
    Debug_print('Error, Parsing input.txt')
    fd_input.close()
    exit()
  _input_params.BuildDictLiveTraffic(lines)

  #Since sunday traffic is needed only for A* search
  if _input_params.GetAlgo() == 'A*':
    offset = OFFSETLIVETRAFFIC + num_live_trafficlines
    try:
      num_sunday_trafficlines = int(lines[offset])
      _input_params.SetSundayTrafficLines(num_sunday_trafficlines)
    except ValueError:
      Debug_print('Error, Parsing input.txt')
      fd_input.close()
      exit()
    _input_params.BuildDictSundayTraffic(lines)
  fd_input.close()

def Expand(_input_params, currnode):
  """ Returns a copy of the childrens of the currnode.
      The returned list is the order of occurence in input.txt 
      Example return value : [(B,5),(C,3)] """
  currnodeState = currnode.GetState()
  if currnodeState not in _input_params.dict_live_traffic :
    return None    
  children = list(_input_params.dict_live_traffic[currnodeState])
  return children
 

def IsStateExist(state, List):
  """ Returns True if state exists in openList nodes.
      Else returns False """
  for node in List:
    if node.GetState() == state:
      return True
  # Could not find the state
  return False 


def PrintOutputToFile(GoalNodeId, NodeRepository, fd_output):
  """ Traces back the path from the goal to the source
      and prints the same to the output.txt file"""
  global ROOTNODEID
  stackTraceBack = []
  nodeId = GoalNodeId
  while 1:
     node = NodeRepository[nodeId]
     stackTraceBack.append('%s %d\n'%(node.GetState(), node.GetG()) )
     parentNodeId = node.GetParentNodeID()
     if parentNodeId == ROOTNODEID:
       # Means node now is root, hence break
       break
     elif parentNodeId < 0:
       # Something went wrong
       print('Error, Could not trace back the source from goal')
       fd_output.close()
       exit()
     nodeId = parentNodeId
  while stackTraceBack:
    line = stackTraceBack.pop()
    fd_output.write(line)
    #print line,
  fd_output.close()


def BFSSearch(_input_params):
  """ Implements and outputs BFS search results """
  global ROOTNODEID
  nodeCount = 1
  fd_output = open('output.txt', 'w')
  if _input_params.GetStartState() == _input_params.GetGoalState():
    fd_output.write('%s %d\n'%(_input_params.GetStartState(), 0) )
    fd_output.close()
    return
  openList = deque() #Queue of nodes
  closedList = [] #List of nodes
  NodeRepository = {}
  RootNode = _Node()
  #TODO: IMP. setting parent's node Id as ROOTNODEID for rootnode. 
  RootNode.SetNodeValues(nodeCount, _input_params.GetStartState(), 0, ROOTNODEID)
  nodeCount += 1
  openList.append(RootNode)
  NodeRepository[RootNode.GetNodeId()] = RootNode
  while 1:
    if len(openList) == 0:
      print('Failed to find the solution.\n')
      fd_output.close()
      return
    currnode = openList.popleft() # Always remove from front
    if currnode.GetState() == _input_params.GetGoalState():
      # We reached the goal
      PrintOutputToFile(currnode.GetNodeId(), NodeRepository, fd_output)
      return
    closedList.append(currnode)
    children = Expand(_input_params, currnode)
    if children is not None:
      for i in range(len(children)):
        child = children[i]
        state = child[0]
        cost = child[1]
        # To avoid loops
        if ((not IsStateExist(state, openList)) and 
           (not IsStateExist(state, closedList))):
          node = _Node()
          g = currnode.GetG() + cost
          node.SetNodeValues(nodeCount, state, g, currnode.GetNodeId())
          nodeCount += 1
          openList.append(node) # FIFO for BFS
          NodeRepository[node.GetNodeId()] = node
  fd_output.close()
  
  

def DFSSearch(_input_params):
  """ Implements and outputs DFS search results """
  global ROOTNODEID
  nodeCount = 1
  fd_output = open('output.txt', 'w')
  if _input_params.GetStartState() == _input_params.GetGoalState():
    fd_output.write('%s %d\n'%(_input_params.GetStartState(), 0) )
    fd_output.close()
    return
  openList = deque() #Stack of nodes. But removed from front
  closedList = [] #List of nodes
  NodeRepository = {}
  RootNode = _Node()
  #TODO: IMP. setting parent's node Id as ROOTNODEID for rootnode. 
  RootNode.SetNodeValues(nodeCount, _input_params.GetStartState(), 0, ROOTNODEID)
  nodeCount += 1
  openList.appendleft(RootNode)
  NodeRepository[RootNode.GetNodeId()] = RootNode
  while 1:
    if len(openList) == 0:
      print('Failed to find the solution.\n')
      fd_output.close()
      return
    currnode = openList.popleft() # Always remove from front
    if currnode.GetState() == _input_params.GetGoalState():
      # We reached the goal
      PrintOutputToFile(currnode.GetNodeId(), NodeRepository, fd_output)
      return
    closedList.append(currnode)
    children = Expand(_input_params, currnode)
    if children is not None:
      # To make sure highest priority child is at the top of stack, we reverse
      for child in reversed(children):
        state = child[0]
        cost = child[1]
        # To avoid loops
        if((not IsStateExist(state, openList)) and 
           (not IsStateExist(state, closedList))):
          node = _Node()
          g = currnode.GetG() + cost
          node.SetNodeValues(nodeCount, state, g, currnode.GetNodeId())
          nodeCount += 1
          openList.appendleft(node) # LIFO for DFS
          NodeRepository[node.GetNodeId()] = node
  fd_output.close()


def PathCostNode(state, List):
  """ Returns the path cost of Node with state (argument-1) in List (argument-2) """
  for node in List:
    if node.GetState() == state:
      return node.GetG()
  # Could not find the state
  print('Error, couldnot find the state %s'%(state))
  return  


def DeleteNode(state, List):
  """ Delets the node with state (argument-1) from the List (argument-2)"""
  for node in List:
    if node.GetState() == state:
      List.remove(node)
      return
  # Could not find the state
  print('Error, couldnot find the state %s'%(state))
  return


def UCSSearch(_input_params):
  """ Implements and outputs UCS search results """
  global ROOTNODEID
  nodeCount = 1
  fd_output = open('output.txt', 'w')
  if _input_params.GetStartState() == _input_params.GetGoalState():
    fd_output.write('%s %d\n'%(_input_params.GetStartState(), 0) )
    fd_output.close()
    return
  openList = [] #Sorted List of nodes (Frontier)
  closedList = [] #Explored List of nodes
  NodeRepository = {}
  RootNode = _Node()
  #TODO: IMP. setting parent's node Id as ROOTNODEID for rootnode. 
  RootNode.SetNodeValues(nodeCount, _input_params.GetStartState(), 0, ROOTNODEID)
  nodeCount += 1
  openList.append(RootNode)
  NodeRepository[RootNode.GetNodeId()] = RootNode
  while 1:
    if len(openList) == 0:
      print('Failed to find the solution.\n')
      fd_output.close()
      return
    currnode = openList.pop(0) # Always remove from front
    if currnode.GetState() == _input_params.GetGoalState():
      # We reached the goal
      PrintOutputToFile(currnode.GetNodeId(), NodeRepository, fd_output)
      return
    
    children = Expand(_input_params, currnode)
    if children is not None:
      for i in range(len(children)):
        child = children[i]
        state = child[0]
        cost = child[1]
        # To avoid loops
        if ((not IsStateExist(state, openList)) and
           (not IsStateExist(state, closedList))):
          node = _Node()
          g = currnode.GetG() + cost
          node.SetNodeValues(nodeCount, state, g, currnode.GetNodeId())
          nodeCount += 1
          openList.append(node) # Insert at the End. See stability of sorted() in python.
          NodeRepository[node.GetNodeId()] = node
        elif (IsStateExist(state, openList)):
          if (cost < PathCostNode(state, openList)):
            DeleteNode(state, openList)
            node = _Node()
            g = currnode.GetG() + cost
            node.SetNodeValues(nodeCount, state, g, currnode.GetNodeId())
            nodeCount += 1
            openList.append(node) # Insert at the End. See stability of sorted() in python.
            NodeRepository[node.GetNodeId()] = node
        elif (IsStateExist(state, closedList)):
          if (cost < PathCostNode(state, closedList)):
            DeleteNode(state, closedList)
            node = _Node()
            g = currnode.GetG() + cost
            node.SetNodeValues(nodeCount, state, g, currnode.GetNodeId())
            nodeCount += 1
            openList.append(node) # Insert at the End. See stability of sorted() in python.
            NodeRepository[node.GetNodeId()] = node
    closedList.append(currnode)
    openList.sort(key=lambda i: i.g)
  fd_output.close()


def ASTARSearch(_input_params):
  print 'TODO'


def main():
  _input_params = _InputParams()
  ParseInputFile(_input_params)
  #_input_params.DisplayInputParams()
  searchAlgo = _input_params.GetAlgo()
  if searchAlgo == 'BFS':
    BFSSearch(_input_params)
  elif searchAlgo == 'DFS':
    DFSSearch(_input_params)
  elif searchAlgo == 'UCS':
    UCSSearch(_input_params)
  elif searchAlgo == 'A*':
    ASTARSearch(_input_params)
  else:
    print('Wrong search Algo')


if __name__ == '__main__':
  main()
