#!/usr/bin/env python

import sys
import copy


MODES = ('MINIMAX', 'ALPHABETA', 'COMPETITION')
YOUPLAYS = ('X', 'O', 'x', 'o')
_DEBUG_ENABLE = True
MAX_GAMESCORE = 133850
MIN_GAMESCORE = -MAX_GAMESCORE

def Debug_print(msg):
  """ Method to print the debug messages """
  global _DEBUG_ENABLE
  if _DEBUG_ENABLE is True:
    print 'DEBUG:'+ msg


class _Node(object):
  """ Stores the state information """
  def __init__(self):
    self.n = 0
    self.depth = 0
    self.Nodeplayer = None
    self.state = []
    self.gamescore = 0
    self.stake_children_list = []
    self.raid_children_list = []

  def CalculateGameScore(self):
    """ calculates the game score for self.player """
    NodeplayerScore = 0
    oponentScore = 0
    for row in range(self.n):
      for column in range(self.n):
        if self.state[row][column][1] == self.Nodeplayer:
          NodeplayerScore = NodeplayerScore + self.state[row][column][0]
        elif self.state[row][column][1] != '.':
          oponentScore = oponentScore + self.state[row][column][0]
    self.gamescore = NodeplayerScore - oponentScore

  def BuildStakeChildrenList(self, _input):
    for row in range(self.n):
      for column in range(self.n):
        if self.state[row][column][1] == '.':
          # Here we realize that there exists a child
          newNode = _Node()
          newNode.n = self.n
          newNode.depth = self.depth+1
          newNode.state = copy.deepcopy(self.state)
          if self.Nodeplayer in ('X','x'):
            newNode.state[row][column][1] = 'X'
            newNode.Nodeplayer = 'O'
          elif self.Nodeplayer in ('O','o'):
            newNode.state[row][column][1] = 'O'
            newNode.Nodeplayer = 'X'
          else:
            print 'Something went wrong in Boardstate'
          if newNode.depth == _input.depth : 
            newNode.CalculateGameScore()
          self.stake_children_list.append(newNode) 

  def BuildRaidChildrenList(self):
     """ TODO """

  def DisplayNode(self):
    print 'Nodeplayer:%s;gamescore:%d'%(self.Nodeplayer,self.gamescore)
    for row in range(self.n):
      for column in range(self.n):
        #sys.stdout.write('%s'%self.state[row][column])
        print self.state[row][column],
      print


class _Input(object):
  """ Stores the input.txt """
  def __init__(self):
    self.n = 0 # board width height
    self.mode = None
    self.youplay = None
    self.depth = 0
    #self.cellvalues = [[] for i in range(self.n)] #list of lists
    #self.boardstate = [[] for i in range(self.n)] #list of lists
    self.cellvalues = []
    self.boardstate = []

  def BuildCellValues(self, lines):
    for linenum in range(4, (4+self.n) ):
      #print 'linenum',linenum
      line = lines[linenum]
      temp = line.split()
      if len(temp) != self.n:
        Debug_print('Error while reading cell value')
        exit()
      local_row = []
      for column in range(self.n):
	try:
          value = int(temp[column])
          local_row.append(value)
        except ValueError:
	  Debug_print('Error converting int value of a cell')
      self.cellvalues.append(local_row) 

  def BuildBoardState(self, lines):
    for linenum in range((4+self.n) , (4+self.n+self.n)):
      #print 'linenum',linenum
      line = lines[linenum]
      temp = list(line)
      if len(temp) is not self.n:
        Debug_print('Error while reading cell value')
        exit()
      local_row = []
      for column in range(self.n):
        statevalue = temp[column]
        if statevalue not in YOUPLAYS:
          if statevalue is not '.':
            Debug_print('Error in state')
        local_row.append(statevalue)
      self.boardstate.append(local_row)


  def Display_Input(self):
    """ Displays the parsed values """
    print'**************_InputParams**************'
    print'%-15s'%'n',':','%d'%self.n
    print'%-15s'%'mode',':','%s'%self.mode
    print'%-15s'%'youplay',':','%s'%self.youplay
    print'%-15s'%'depth',':','%d'%self.depth
    for row in range(len(self.cellvalues)):
      for column in range(len(self.cellvalues[row])):
        #print self.cellvalues[row][column],None
        sys.stdout.write('%d '%self.cellvalues[row][column])
      print 
    for row in range(len(self.boardstate)):
      for column in range(len(self.boardstate[row])):
        #print self.cellvalues[row][column],None
        sys.stdout.write('%s '%self.boardstate[row][column])
      print 
    print'****************************************' 


def BuildRootNode(_input, rootNode):
  """ Builds the root node """
  rootNode.n = _input.n
  rootNode.depth = 0
  rootNode.Nodeplayer = _input.youplay
  for row in range(_input.n):
    local_list = []
    for column in range(_input.n):
      local_tuplelike = [_input.cellvalues[row][column], _input.boardstate[row][column]]
      local_list.append(local_tuplelike)
    rootNode.state.append(local_list)


def DisplayChildren(nodeToDisplay):
  """ Debug func to display the children """
  for node in nodeToDisplay.stake_children_list:
    node.DisplayNode()

def ParseInputFile(_input):
  """ Parses the input file """
  fd_input = open('input.txt', 'rU')
  lines = fd_input.read().split('\n')
  print(lines)
  #print 'len:%d'%len(lines)
  try:
    n = int(lines[0])
    _input.n = n
  except ValueError:
    Debug_print('Error, Parsing input.txt')
    fd_input.close()
    exit()
  mode = lines[1]
  if mode not in MODES:
    Debug_print('Error, Parsing mode in input.txt')
    fd_input.close()
    exit()
  _input.mode = mode
  youplay = lines[2]
  if youplay not in YOUPLAYS:
    Debug_print('Error, Parsing youplay in input.txt')
    fd_input.close()
    exit()
  _input.youplay = youplay 
  try:
    depth = int(lines[3])
    _input.depth = depth
  except ValueError:
    Debug_print('Error, Parsing input.txt')
    fd_input.close()
    exit() 
  _input.BuildCellValues(lines)
  _input.BuildBoardState(lines)


def main():
  _input = _Input()
  ParseInputFile(_input)
  _input.Display_Input()
  rootNode = _Node()
  BuildRootNode(_input, rootNode)
  rootNode.CalculateGameScore()
  rootNode.DisplayNode()
  rootNode.BuildStakeChildrenList(_input)
  DisplayChildren(rootNode)

if __name__ == '__main__':
  main()
