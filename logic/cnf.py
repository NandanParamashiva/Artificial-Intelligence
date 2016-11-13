#! /usr/bin/env python

import sys
import ply.lex as lex
import re
import copy

data = '''(A(x,John) & ~B(Bob))=> C (x)'''

class PredicateObj(object):
  def __init__(self,predicate=None,args=None,neg=False):
    self.predicate = predicate
    self.args = args
    self.neg = neg


tokens = ('LPAREN','RPAREN','NOT','AND','OR','IMPLIES','PREDICATE',)

# Regular expression rules
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_NOT     = r'~'
t_AND     = r'&'
t_OR      = r'\|'
t_IMPLIES = r'=>'

# Predicate token rule
def t_PREDICATE(t):
  r'([A-Z]\w*)\s*\(([^&\|=>\)]+)\)' #TODO: REVISIT
  match = re.match(r'([A-Z]\w*)\s*\(([^&\|=>\)]+)\)',t.value)
  if not match:
    print'Something went wrong in tokonizing'
  predicate = match.group(1).strip()
  args = match.group(2)
  splitlist = args.split(',')
  argslist = []
  for item in splitlist:
    if (re.search(r'[A-Z]',item)):
      # means item is constant
      argslist.append((item.strip(),'CONSTANT'))
    else:
      argslist.append((item.strip(),'VARIABLE'))
  t.value = PredicateObj(predicate,argslist,False)
  return t
  
t_ignore  = ' \t'

# Error handling 
def t_error(t):
    print("ERROR: invalid character '%s'" % t.value[0])
    exit()
    t.lexer.skip(1)

# Build lexer
lexer = lex.lex()


###########################################
#### YACC: Rules for Parsing are below ####
###########################################

# TODO: () precedence should be entered below?
precedence = (
    ('left','IMPLIES'),
    ('left','OR'),
    ('left','AND'),
    ('left','NOT'),
    )

class ClauseObj(object):
  def __init__(self,
               operator         =None,
               left_clause      =None,
               right_clause     =None,
               predicate_clause =None,
               neg              =False):
    self.operator = operator
    self.left_clause = left_clause
    self.right_clause = right_clause
    self.predicate_clause = predicate_clause
    self.neg = neg

def p_expression_logic_op(p):
    '''expression : expression AND expression
                  | expression OR expression'''

    p[0] = ClauseObj(p[2],p[1],p[3],None,False)

#TODO: Test this
def p_expression_implies(p):
    'expression : expression IMPLIES expression'
    # A=>B is ~A|B
    #p[0] = ClauseObj('OR',ClauseObj(None,None,None,p[1],True),p[3],None,False)
    if p[1].neg == False:
      p[1].neg = True
    else:
      p[1].neg = False
    p[0] = ClauseObj('|',p[1],p[3],None,False)

def p_expression_not(p):
    'expression : NOT expression'
    #p[0] = ClauseObj(None,None,None,p[2],True)
    if p[2].neg == False:
      p[2].neg = True
    else:
      p[2].neg = False
    p[0] = p[2]

def p_expression_brackets(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_predicate(p):
    'expression : PREDICATE'
    p[0] = ClauseObj(None,None,None,p[1],False)

# Syntax errors rule
def p_error(p):
    print("ERROR:Syntax error in input!")
    exit()

import ply.yacc as yacc
yacc.yacc()


def BuildPredicateClauseString(root):
    string = ""
    if root.neg == True:
      string += "~"
    string += "%s("%root.predicate_clause.predicate
    for i in range(len(root.predicate_clause.args)-1):
      string += "%s,"%root.predicate_clause.args[i][0]
    string += "%s)"%(root.predicate_clause.args[-1][0])
    return string


def BuildBinOpClauseString(root):
    string = ""
    if root.neg == True:
      string += "~"
    string += "(%s%s%s)"%(
                        PrintTreeTraversal(root.left_clause),
                        root.operator,
                        PrintTreeTraversal(root.right_clause)
                       )
    return string


def PrintTreeTraversal(root):
  if root==None:
    return None
  elif((root.operator    == None) or 
      (root.left_clause  == None) or 
      (root.right_clause == None)):
    ''' Then we assume This ClauseObj is PredicateObj'''
    if root.predicate_clause != None:
      return BuildPredicateClauseString(root)
    else:
      print'ERROR:ClauseObj should have either operator or PredicateObj'
      exit()
  elif(root.operator != None):
    # If here, it means root is a ClauseObj with Binary operator
    return BuildBinOpClauseString(root) 
  else:
    print'ERROR:Something went wrong'
    exit()


def DisplayTree(result):
    finaloutput = PrintTreeTraversal(result)
    for char in finaloutput:
      if char == '[' or char == ']':
        finaloutput = finaloutput.replace(char,'')
    print finaloutput

def RoughDisplaySentences(result):
    finaloutput = PrintTreeTraversal(result)
    for char in finaloutput:
      if char == '[' or char == ']':
        finaloutput = finaloutput.replace(char,'')
    sentence_list = finaloutput.split('&')
    print 'Sentences in KB:'
    for i in range(len(sentence_list)):
      print '%d:%s'%(i+1,sentence_list[i])


def NegateTrueFalse(x):
  if x == True:
    x = False
  elif x == False:
    x = True
  else:
    print 'ERROR: Neither True nor False'
    exit()
  return x

def FlipAndOrOperator(x):
  if x == '&':
    x = '|'
  elif x == '|':
    x = '&'
  else:
    print 'ERROR: BinOp should be either & or | in Tree'
    exit()
  return x

def MoveNegDownTheTree(root):
  if root == None:
    return
  elif root.operator == None:
    #Means we are the predicate clause so just return
    return
  else:
    #If we are here, it should be a Binary op object
    if root.operator == None:
      print 'ERROR: Something went wrong'
      exit()
    if root.neg == True:
      root.neg = False
      root.operator = FlipAndOrOperator(root.operator)
      root.left_clause.neg = NegateTrueFalse(root.left_clause.neg)
      root.right_clause.neg = NegateTrueFalse(root.right_clause.neg)
    MoveNegDownTheTree(root.left_clause)
    MoveNegDownTheTree(root.right_clause)


SETTLED_DOWN = False

def LeftBranchAND(root):
        # Case 1
        global SETTLED_DOWN
        root.operator = '&'
        root.left_clause.operator = '|'
        new_copy_branch = copy.deepcopy(root.right_clause)
        temp = root.left_clause.right_clause
        root.left_clause.right_clause = root.right_clause
        new_node = ClauseObj('|',temp,new_copy_branch,None,False)
        root.right_clause = new_node
        SETTLED_DOWN = False
        
def RightBranchAND(root):
        # Case 2
        root.operator = '&'
        root.right_clause.operator = '|'
        new_copy_branch = copy.deepcopy(root.left_clause)
        temp = root.right_clause.left_clause
        root.right_clause.left_clause = root.left_clause
        new_node = ClauseObj('|',new_copy_branch,temp,None,False)
        root.left_clause = new_node
        SETTLED_DOWN = False

def ConvertToCNF(root):
  global SETTLED_DOWN
  ''' Converts the given tree to CNF form '''
  if root == None:
    return
  elif ((root.operator == None) and 
        (root.predicate_clause != None)
       ):
    return
  else:
    ''' If here, means the root obj is binary clause obj '''
    if ((root.operator == None) or 
        (root.predicate_clause != None)
       ):
        # Double check: We expect predicate clause to be None. 
        print'ERROR: Something went wrong' 
        exit()
    if ((root.operator == '|') and 
        (root.left_clause.operator == '&')
        ): # Case 1
        LeftBranchAND(root)
    elif ((root.operator == '|') and
          (root.right_clause.operator == '&')
          ): # Case 2
          RightBranchAND(root)
    ConvertToCNF(root.left_clause)
    ConvertToCNF(root.right_clause)
    return


def BuildSentences(root, sentences_list):
  if root == None:
    return
  elif ((root.operator == None) and 
        (root.predicate_clause != None)
       ):
    sentences_list.append(root)
    return
  else:
    # If here, means, root is binary op
    if root.operator == '|':
      # Below this root, we should not see a '&' 
      # (since we have distributed it down the tree)
      sentences_list.append(root)
      return
    elif root.operator == '&':
      BuildSentences(root.left_clause,sentences_list)
      BuildSentences(root.right_clause,sentences_list)
    else:
      print 'ERROR:Something went wrong'
      exit()

class _Input(object):
  """ Stores the input.txt """
  def __init__(self):
    self.total_queries = 0 #Number of queries
    self.query_list = [] #Each element is a clause object pointing to Predicate
    self.total_sent_lines = 0 #Input lines
    self.sent_lines_list = [] #

def BuildPredicateObj(line, pattern):
      match = pattern.search(line)
      if not match:
        print'ERROR: Pattern didnot match'
        return None
      predicate = match.group(1).strip()
      args = match.group(2)
      splitlist = args.split(',')
      argslist = []
      for item in splitlist:
        if (re.search(r'[A-Z]',item)):
          # means item is constant
          argslist.append((item.strip(),'CONSTANT'))
        else:
          argslist.append((item.strip(),'VARIABLE'))
      predicate_object = PredicateObj(predicate,argslist,False)
      return predicate_object

def BuildQueryList(_input,lines):
  #pattern = r'\s*([A-Z]\w*)\s*\(([^&\|=>\)]+)\)'
  pattern = re.compile(r'\s*([A-Z]\w*)\s*\(([^&\|=>\)]+)\)')
  #neg_pattern = r'\s*~\s*\(?([A-Z]\w*)\s*\(([^&\|=>\)]+)\)'
  for linenum in range(1, _input.total_queries+1):
    line = lines[linenum]
    predicate_object = BuildPredicateObj(line,pattern)
    if (predicate_object == None):
      print 'ERROR: Error in query %s'%line
      continue
    if re.search(r'~',line):
      clause_object = ClauseObj(None,None,None,predicate_object,True)
    else:
      clause_object = ClauseObj(None,None,None,predicate_object,False)
    _input.query_list.append(clause_object) 

def DisplayQueryList(_input):
  for i in range(_input.total_queries):
    print 'Given Query%d:'%i,
    DisplayTree(_input.query_list[i]) 
    
def BuildSentLineList(_input,lines):
  for linenum in range(_input.total_queries+2, _input.total_queries+2+_input.total_sent_lines):
    line = lines[linenum]
    _input.sent_lines_list.append(line.strip())

def DisplaySentLineList(_input):
  for i in range(_input.total_sent_lines):
    print 'Given Sentence%d:'%i , _input.sent_lines_list[i]

def ParseInputFile(_input):
  """ Parses the input file """
  fd_input = open('input.txt', 'rU')
  lines = fd_input.read().split('\n')
  #print(lines)
  #print 'len:%d'%len(lines)
  try:
    nq = int(lines[0])
    _input.total_queries = nq
  except ValueError:
    print 'Error, Parsing nq in input.txt'
    fd_input.close()
    exit()
  BuildQueryList(_input,lines)
  try:
    ns = int(lines[_input.total_queries+1])
    _input.total_sent_lines = ns
  except ValueError:
    print 'Error, Parsing ns in input.txt'
    fd_input.close()
    exit()
  BuildSentLineList(_input,lines)
  

def main():
  global SETTLED_DOWN
  _input = _Input()
  ParseInputFile(_input)
  DisplayQueryList(_input)
  DisplaySentLineList(_input)
  for i in range(_input.total_sent_lines):
        print'\n\n*****************************'
        print'Given Sentence%d: %s'%(i,_input.sent_lines_list[i])
        root = yacc.parse(_input.sent_lines_list[i])
        #from pprint import pprint
        #pprint (vars(result))
        MoveNegDownTheTree(root)
        print'----------------------------'
        print'Before Distributing | over &'
        DisplayTree(root)
        #print'----------------------------'
        SETTLED_DOWN = False
        while (SETTLED_DOWN == False):
          SETTLED_DOWN = True
          ConvertToCNF(root)
        print'----------------------------'
        print'After Distributing | over &'
        DisplayTree(root)
        #print'----------------------------'
        #RoughDisplaySentences(root)
        sentences_list = []
        BuildSentences(root,sentences_list)
        print'----------------------------'
        print'Sentences:'
        for i in range(len(sentences_list)):
          DisplayTree(sentences_list[i])
        print'*****************************'


if __name__ == '__main__':
  main()

