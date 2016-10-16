#!/usr/bin/env python

import sys
import copy
import time

"""
TODO:
1. DONE
If your raid is not conquering then no need to raid. i.e no need to consider that state.
Because, that state will anyway be covered in stake.
Remember, stake has higher priority over raid.

2. DONE
Check the priority order:
-Stake > Raid
-Top Left to Right Bottom

3. DONE
Only one square/unoccupied space is left, but your input file has
depth as 2.
(Need to handle such cases)

4.

"""

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
    self.stake_children_list = [] #insert front. And remove from end. FIFO
    self.raid_children_list = [] #insert front. And remove from end. FIFO
    self.stakeORraid = None
    self.stakeORraidLocation = None

  def DisplayBoardState(self):
    """ Displays board state only, according to the HW specification """
    for row in range(self.n):
      for column in range(self.n):
        print '%s'%self.state[row][column][1],
      print

  def OutputBoardState(self, fd_output):
    """ writes board state only to output.txt, according to the HW specification """
    for row in range(self.n):
      for column in range(self.n):
        fd_output.write('%s'%self.state[row][column][1])
      fd_output.write('\n')

  def OutputMove(self, fd_output):
    """ writes the move only, according to HW spec """
    fd_output.write('%s %s\n'%(self.stakeORraidLocation, self.stakeORraid))

  def CalculateGameScore(self, _input):
    """ calculates the game score for self.player """
    NodeplayerScore = 0
    oponentScore = 0
    for row in range(self.n):
      for column in range(self.n):
        if self.state[row][column][1] == _input.youplay:
          NodeplayerScore = NodeplayerScore + self.state[row][column][0]
        elif self.state[row][column][1] != '.':
          oponentScore = oponentScore + self.state[row][column][0]
    self.gamescore = NodeplayerScore - oponentScore

  def makeNode(self, newrow, newcolumn, _input, stakeORraid):
      """ returns a newNode.
      input:  - newrow/newcolumn:Position where the current player i.e
                the Nodeplayer wants to move(raid)/create(stake). Hence,
                if self.Nodeplayer is X then the above new position is
                marked with X
              - Note that newNode's Nodeplayer is swapped.
      output: - stake and raid children list is still empty.
              - gamescore is populated only if its the leaf children.
              - Rest of the elements of _Node() are populated """
      newNode = _Node()
      newNode.stakeORraidLocation = '%s%d'%((chr(ord('A')+newcolumn)), (newrow+1))
      newNode.stakeORraid = stakeORraid
      newNode.n = self.n
      newNode.depth = self.depth+1
      newNode.state = copy.deepcopy(self.state)
      if self.Nodeplayer in ('X','x'):
        newNode.state[newrow][newcolumn][1] = 'X'
        newNode.Nodeplayer = 'O'
      elif self.Nodeplayer in ('O','o'):
        newNode.state[newrow][newcolumn][1] = 'O'
        newNode.Nodeplayer = 'X'
      else:
        print 'Something went wrong in Boardstate'
      if newNode.depth == _input.depth :
        newNode.CalculateGameScore(_input)
      return newNode

  def BuildStakeChildrenList(self, _input):
    for row in range(self.n):
      for column in range(self.n):
        if self.state[row][column][1] == '.':
          # Here we realize that there exists a child
          newNode = self.makeNode(row, column, _input, 'Stake')
          self.stake_children_list.insert(0, newNode) 

  def isLocationEmpty(self, newLoc):
    """ returns True if newLoc(tuple) is empty """
    row = newLoc[0]
    column = newLoc[1]
    if self.state[row][column][1] == '.':
      return True
    else:
      return False

  def isValidLocation(self, newLoc):
    """ Returns True if newLoc is valid """
    row = newLoc[0]
    column = newLoc[1]
    if ((row < 0) or (row >= self.n)):
      return False
    elif ((column < 0) or (column >= self.n)):
      return False
    else:
      return True

  def getAdjacentLocation(self, row, column):
    """ Returns the adjacent locations of (row,column).
        New locations are tuple of tuple (up,down,left,right) i.e
       ((row,column),(row,column)..) """
    up = (row-1,column)
    down = (row+1,column)
    left = (row,column-1)
    right = (row,column+1)
    return (up,left,right,down)

  def isOccupiedByOpponent(self, newLoc, opponent):
    """ Returns True if newLoc is occupied by opponent """
    newrow = newLoc[0]
    newcolumn = newLoc[1]
    if self.state[newrow][newcolumn][1] == '.':
      return False
    elif(self.state[newrow][newcolumn][1] == opponent):
      return True
    else:
      return False

  def conquer(self, newrow, newcolumn, _input, curPlayer):
    """ This is called only within raidLocation function.
        This function checks if the adjacent positions of
        (newrow,newcolumn) belongs to oponent. If it does,
        this function replaces the oponent symbol with the 
        self.Nodeplayer i.e currplayers symbol (X/O).
        Since, the game state is changed, gamescore calculator
        function is called to update the gamescore. 
    """
    adjacentLocs = self.getAdjacentLocation(newrow, newcolumn)
    for i in range(4): #up,down,left,right
      if self.isValidLocation(adjacentLocs[i]):
        #Since conquer is called on newNode, the self will have opponent symbol
        opponentSymbol = self.Nodeplayer
        if self.isOccupiedByOpponent(adjacentLocs[i], opponentSymbol):
          #We conquer here
          row = adjacentLocs[i][0]
          column = adjacentLocs[i][1]
          self.state[row][column][1] = copy.copy(curPlayer) 
          #Since the game changes on raid, we recalculate the gamescore
          if self.depth == _input.depth : #TODO: Is this if check needed?
            self.CalculateGameScore(_input)

  def raidLocation(self, newrow, newcolumn, _input):
    """ Raids the location newLoc and also conquers the neighbours, if any.
        Note that each of this raidLocation creates a new child and appends
        to the raid_children_list.
        Note: _input is needed to get the depth of tree """
    newNode = self.makeNode(newrow, newcolumn, _input, 'Raid')
    newNode.conquer(newrow, newcolumn, _input, self.Nodeplayer)
    self.raid_children_list.insert(0, newNode)

  def isLocationOccupiedByPlayerSymbol(self, Loc, playersymbol):
    """ Returns True if PlayerSymbol has occupied the Loc """
    row = Loc[0]
    column = Loc[1]
    if self.state[row][column][1] == playersymbol:
      return True
    else:
      return False

  def isSurrondedByOpponent(self, row, column):
    """ Returns True of surrronded by opponent """
    if self.Nodeplayer in ('X','x'):
      opponent = 'O'
    elif self.Nodeplayer in ('O','o'):
      opponent = 'X'
    else:
      print 'Shouldnot be here'
      exit()
    adjLocs = self.getAdjacentLocation(row,column)
    for i in range(4): #up,down,left,right
      if (self.isValidLocation(adjLocs[i])) :
        if (self.isLocationOccupiedByPlayerSymbol(adjLocs[i], opponent)):
          return True
    return False

  def isRaidPossible(self, currow, curcolumn):
    """ Returns True if given (currow, curcolumn) is raidable.
        Raid without conquer(see TODO#1 at file begining) :
        Note that, even if (currow,curcolumn) has a neighbour own player,
        we do not return True right away, instead we see if the (currow,curcolumn)
        also has an opponent in neighbour, only then (both the conditions are met)
        we return True. This is because of Performance reason. """
    surrondedByOpponent = self.isSurrondedByOpponent(currow, curcolumn)
    adjLocs = self.getAdjacentLocation(currow,curcolumn)
    for i in range(4): #up,down,left,right
      if (self.isValidLocation(adjLocs[i])) :
        if (self.isLocationOccupiedByPlayerSymbol(adjLocs[i], self.Nodeplayer)):
           #TODO: Is it ok to have this check?
           if (surrondedByOpponent): # return true only if there is also an opponent surronding this currow,curcolumn
             return True
    #couldnot find my own player and opponent in neighbour hence cannot raid this location
    return False

  def BuildRaidChildrenList(self, _input):
    for row in range(self.n):
      for column in range(self.n):
        if self.state[row][column][1] == '.':
          if(self.isRaidPossible(row, column)):
            self.raidLocation(row, column, _input)
          
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
    self.initialEmptySpaces = 0

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
        if statevalue == '.':
          self.initialEmptySpaces = self.initialEmptySpaces + 1
        if statevalue not in YOUPLAYS:
          if statevalue is not '.':
            Debug_print('Error in state')
            exit()
        local_row.append(statevalue)
      self.boardstate.append(local_row)


  def Display_Input(self):
    """ Displays the parsed values """
    print'----------_InputParams----------'
    print'%-10s'%'n',':','%d'%self.n
    print'%-10s'%'mode',':','%s'%self.mode
    print'%-10s'%'youplay',':','%s'%self.youplay
    print'%-10s'%'depth',':','%d'%self.depth
    for row in range(len(self.cellvalues)):
      for column in range(len(self.cellvalues[row])):
        #print self.cellvalues[row][column],None
        sys.stdout.write('%d '%self.cellvalues[row][column])
      print 
    for row in range(len(self.boardstate)):
      for column in range(len(self.boardstate[row])):
        #print self.cellvalues[row][column],None
        sys.stdout.write('%s'%self.boardstate[row][column])
      print
    print'%-10s'%'initialEmptySpaces',':','%d'%self.initialEmptySpaces
    print'--------------------------------' 


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
  print'Stake children'
  for node in nodeToDisplay.stake_children_list:
    node.DisplayNode()
  print'Raid children'
  for node in nodeToDisplay.raid_children_list:
    node.DisplayNode()

def ParseInputFile(_input):
  """ Parses the input file """
  fd_input = open('input.txt', 'rU')
  lines = fd_input.read().split('\n')
  #print(lines)
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


def minimax(rootNode, _input):
  """ Implements the minimax algo """
  curEmptySpaces = (_input.initialEmptySpaces - rootNode.depth)
  if ((rootNode.depth >= _input.depth) or (curEmptySpaces <= 0)):
    # ideally, it should not end here since input depth != 0
    rootNode.CalculateGameScore(_input)
    return rootNode
  rootNode.BuildStakeChildrenList(_input)
  rootNode.BuildRaidChildrenList(_input)
  #DisplayChildren(rootNode)
  v = MIN_GAMESCORE
  resultNode = None
  for i in reversed(range(len(rootNode.stake_children_list))):
    temp = max(v, MinValue(rootNode.stake_children_list[i], _input))
    if temp > v:
      v = temp
      resultNode = rootNode.stake_children_list[i]
  for i in reversed(range(len(rootNode.raid_children_list))):
    temp = max(v, MinValue(rootNode.raid_children_list[i], _input))
    if temp > v:
      v = temp
      resultNode = rootNode.raid_children_list[i]
  return resultNode


def MinValue(node, _input):
  curEmptySpaces = (_input.initialEmptySpaces - node.depth)
  if ((node.depth >= _input.depth) or (curEmptySpaces <= 0)):
    node.CalculateGameScore(_input)
    return node.gamescore
  node.BuildStakeChildrenList(_input)
  node.BuildRaidChildrenList(_input)
  v = MAX_GAMESCORE
  for i in reversed(range(len(node.stake_children_list))):
    v = min(v, MaxValue(node.stake_children_list[i], _input))
    node.stake_children_list.pop(i)
  for i in reversed(range(len(node.raid_children_list))):
    v = min(v, MaxValue(node.raid_children_list[i], _input))
    node.raid_children_list.pop(i)
  return v


def MaxValue(node, _input):
  curEmptySpaces = (_input.initialEmptySpaces - node.depth)
  if ((node.depth >= _input.depth) or (curEmptySpaces <= 0)):
    node.CalculateGameScore(_input)
    return node.gamescore
  node.BuildStakeChildrenList(_input)
  node.BuildRaidChildrenList(_input)
  v = MIN_GAMESCORE
  for i in reversed(range(len(node.stake_children_list))):
    v = max(v, MinValue(node.stake_children_list[i], _input))
    node.stake_children_list.pop(i)
  for i in reversed(range(len(node.raid_children_list))):
    v = max(v, MinValue(node.raid_children_list[i], _input))
    node.raid_children_list.pop(i)
  return v


def MinValueAlphaBeta(node, _input, alpha, beta):
  # For alphabeta pruning algo
  curEmptySpaces = (_input.initialEmptySpaces - node.depth)
  if ((node.depth >= _input.depth) or (curEmptySpaces <= 0)):
    node.CalculateGameScore(_input)
    return node.gamescore
  node.BuildStakeChildrenList(_input)
  node.BuildRaidChildrenList(_input)
  v = MAX_GAMESCORE
  for i in reversed(range(len(node.stake_children_list))):
    v = min(v, MaxValueAlphaBeta(node.stake_children_list[i], _input, alpha, beta))
    node.stake_children_list.pop(i)
    if v <= alpha:
      return v
    beta = min(beta, v)
  for i in reversed(range(len(node.raid_children_list))):
    v = min(v, MaxValueAlphaBeta(node.raid_children_list[i], _input, alpha, beta))
    node.raid_children_list.pop(i)
    if v <= alpha:
      return v
    beta = min(beta, v)
  return v


def MaxValueAlphaBeta(node, _input, alpha, beta):
  # For alphabeta Pruning algo
  curEmptySpaces = (_input.initialEmptySpaces - node.depth)
  if ((node.depth >= _input.depth) or (curEmptySpaces <= 0)):
    node.CalculateGameScore(_input)
    return node.gamescore
  node.BuildStakeChildrenList(_input)
  node.BuildRaidChildrenList(_input)
  v = MIN_GAMESCORE
  for i in reversed(range(len(node.stake_children_list))):
    v = max(v, MinValueAlphaBeta(node.stake_children_list[i], _input, alpha, beta))
    node.stake_children_list.pop(i)
    if v >= beta:
      return v
    alpha = max(alpha,v)
  for i in reversed(range(len(node.raid_children_list))):
    v = max(v, MinValueAlphaBeta(node.raid_children_list[i], _input, alpha, beta))
    node.raid_children_list.pop(i)
    if v >= beta:
      return v
    alpha = max(alpha,v)
  return v


def AlphaBeta(node, _input):
  """ Implements the AlphaBeta algorithm """
  curEmptySpaces = (_input.initialEmptySpaces - node.depth)
  # Note, node is rootNode here
  if ((node.depth >= _input.depth) or (curEmptySpaces <= 0)):
    # ideally, it should not end here since input depth != 0
    node.CalculateGameScore(_input)
    return node
  node.BuildStakeChildrenList(_input)
  node.BuildRaidChildrenList(_input)
  v = MIN_GAMESCORE
  resultNode = None
  alpha = MIN_GAMESCORE
  beta = MAX_GAMESCORE
  for i in reversed(range(len(node.stake_children_list))):
    temp = max(v, MinValueAlphaBeta(node.stake_children_list[i], _input, alpha, beta))
    if temp > v:
      resultNode = node.stake_children_list[i]
    v = temp
    if v >= beta:
      return resultNode
    alpha = max(alpha,v)
  for i in reversed(range(len(node.raid_children_list))):
    temp = max(v, MinValueAlphaBeta(node.raid_children_list[i], _input, alpha, beta))
    if temp > v:
      resultNode = node.raid_children_list[i]
    v = temp
    if v >= beta:
      return resultNode
    alpha = max(alpha,v)
  return resultNode


def DisplayResult(node):
  """ Displays the final answer """
  print node.stakeORraidLocation, node.stakeORraid


def Output_txt(resultNode,fd_output):
   """ Writes the output.txt """
   resultNode.OutputMove(fd_output)
   resultNode.OutputBoardState(fd_output)


def main():
  _input = _Input()
  ParseInputFile(_input)
  _input.Display_Input()
  rootNode = _Node()
  BuildRootNode(_input, rootNode)
  #rootNode.CalculateGameScore(_input)
  #rootNode.DisplayNode()
  fd_output = open('output.txt', 'w')
  if _input.mode == 'MINIMAX':
    resultNode = minimax(rootNode, _input)
    #print '-------Result------'
    #DisplayResult(resultNode)
    #resultNode.DisplayNode()
    #resultNode.DisplayBoardState()
    Output_txt(resultNode,fd_output)
    #print '-------------------'
  elif _input.mode == 'ALPHABETA':
    resultNode = AlphaBeta(rootNode, _input)
    Output_txt(resultNode,fd_output)
  else:
    print 'competetion mode is not yet supported'
  fd_output.close()
  

if __name__ == '__main__':
  print '****************************************'
  startTimer = time.time()
  main()
  endTimer = time.time()
  print("Time taken: %s seconds" % (endTimer - startTimer))
  print '****************************************'

