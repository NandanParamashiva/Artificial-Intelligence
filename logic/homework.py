#! /usr/bin/env python

import sys
import ply.lex as lex
import re
import copy
import pprint

DEBUG_ENABLE = False
STANDARDIZE_KB_COUNT = 1

def debug_print(msg):
  global DEBUG_ENABLE
  if DEBUG_ENABLE:
    print '%s'%msg

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
  global DEBUG_ENABLE
  if DEBUG_ENABLE:  
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
  
given_sentences_root = []
POSITIVE = 0
NEGATIVE = 1

def Initialize(predicate_hashmap, predicate):
    predicate_hashmap[predicate] = [] 
    for i in range(2): #[[positive_list],[negative_list]]
        predicate_hashmap[predicate].append([])

def FindNewPredicateAndUpdate(root, predicate_hashmap, KB_sentences_list_root):
  if root == None:
      return
  elif (root.operator == None):
      # Means, it's a predicate clause i.e at leaf
      predicate = root.predicate_clause.predicate 
      if (not(predicate in predicate_hashmap)):
        Initialize(predicate_hashmap, predicate)
      if (root.neg == True): #Means negative predicate
          predicate_hashmap[predicate][NEGATIVE].append(KB_sentences_list_root)
      else:
          predicate_hashmap[predicate][POSITIVE].append(KB_sentences_list_root)
      return
  else:
      #means, binary op
      if (root.neg == True): #double checking if there is any negation
          print'ERROR:negations should have been pushed down to leaf'
          exit()
      FindNewPredicateAndUpdate(root.left_clause, predicate_hashmap, KB_sentences_list_root)
      FindNewPredicateAndUpdate(root.right_clause, predicate_hashmap, KB_sentences_list_root)
      return
    
def BuildHashMapOfPredicates(predicate_hashmap, KB_sentences_list):
  for i in range(len(KB_sentences_list)):
    FindNewPredicateAndUpdate(KB_sentences_list[i], predicate_hashmap,KB_sentences_list[i])



def CreateNegQuery(query_clause_obj):
  predicate = copy.deepcopy(query_clause_obj.predicate_clause.predicate)
  args = copy.deepcopy(query_clause_obj.predicate_clause.args)
  new_predicate_obj = PredicateObj(predicate,args,False)
  if (query_clause_obj.neg == True):
    neg_clause_object = ClauseObj(None,None,None,new_predicate_obj,False)
  else:
    neg_clause_object = ClauseObj(None,None,None,new_predicate_obj,True)
  return neg_clause_object

def AddQueryToKB(neg_query_clause_obj, KB_sentences_list, predicate_hashmap):
    # Adding to KB
    KB_sentences_list.append(neg_query_clause_obj)
    # Adding to hashmap
    predicate = copy.deepcopy(neg_query_clause_obj.predicate_clause.predicate)
    if (not(predicate in predicate_hashmap)):
      Initialize(predicate_hashmap, predicate)
    if (neg_query_clause_obj.neg == True): #Means negative predicate
        predicate_hashmap[predicate][NEGATIVE].append(neg_query_clause_obj)
    else:
        predicate_hashmap[predicate][POSITIVE].append(neg_query_clause_obj)
    return 


def GetListFromTree(root, sentence_list):
  if root == None:
    return
  if root.operator == None:# means, predicate clause
    sentence_list.append(root)
    return
  GetListFromTree(root.left_clause, sentence_list)
  GetListFromTree(root.right_clause, sentence_list)
  return sentence_list


def CheckConflictConstants(pred_args, sent_args):
  ''' Returns True if any conflicts '''
  for i in range(len(pred_args)):
    if ((pred_args[i][1] == sent_args[i][1]) and (pred_args[i][1] == 'CONSTANT')): # check if both are Constants
      if (pred_args[i][0] != sent_args[i][0]):
        #means, both are constants but of different const values
        return True
  return False

def PredToUnify(predicate_clause_obj, sentence_list):
  ''' Identifies the ~Predicate to unify and returns that, if not found, it will return None '''
  for i in range(len(sentence_list)): #its a list of predicate clause obj
    if(predicate_clause_obj.predicate_clause.predicate == sentence_list[i].predicate_clause.predicate):
      if(predicate_clause_obj.neg != sentence_list[i].neg): # should be opposite to reduce/cancel out
        pred_args = predicate_clause_obj.predicate_clause.args
        sent_args = sentence_list[i].predicate_clause.args
        if(len(pred_args) == len(sent_args)):
          if (CheckConflictConstants(pred_args, sent_args) == False):
            return sentence_list[i]
  return None

def ChangesToArgs(predicate_clause_obj, pred_in_sent, binding_node_list_predicates, binding_sentence):
  ''' 1. Populates the var/const binding in binding_node_list_predicates , binding_sentence 
      2. PredToUnify() would have identified if these 2 are unifiable. No need to check here again
         Therefore, assume predicate_clause_obj and pred_in_sent are unifiable 
      3. It returns False, if we find conflicting var-->constant mapping. i.e we cannot unify.
         It returns True, if we could unify '''
  pred_args = predicate_clause_obj.predicate_clause.args
  sent_args = pred_in_sent.predicate_clause.args
  if(len(pred_args) != len(sent_args)):
    print'ERROR: Both len should be same'
    exit()
  for i in range(len(pred_args)):
    if (pred_args[i][1] != sent_args[i][1]):
      # variable<-->constant
      if pred_args[i][1] == 'VARIABLE':
        # if here means, pred_args[i][1] is VARIABLE and sent_args[i][1] is CONSTANT
        if pred_args[i][0] in binding_node_list_predicates:
          if(binding_node_list_predicates[pred_args[i][0]][0] != sent_args[i][0]):
            # Cannot unify
            return False
        binding_node_list_predicates[pred_args[i][0]] = (copy.deepcopy(sent_args[i][0]),'CONSTANT')
      else:
        #means, sent_args[i][1] is VARIABLE and pred_args[i][1] is CONSTANT
        if sent_args[i][0] in binding_sentence:
          if(binding_sentence[sent_args[i][0]][0] != pred_args[i][0]):
            # Cannot unify
            return False
        binding_sentence[sent_args[i][0]] = (copy.deepcopy(pred_args[i][0]),'CONSTANT')
    elif(pred_args[i][1] == 'VARIABLE'):# TODO: Dont know if we have to do this 
        binding_node_list_predicates[pred_args[i][0]] = (copy.deepcopy(sent_args[i][0]),'VARIABLE')
  return True


def BuildNewnodeListPredicates(node_list_predicates, 
                               predicate_clause_obj, #predicate in node_list_predicates that needs to be skipped in newnode
                               sentence, 
                               pred_in_sent,# predicate in sentence that needs to be skipped in newnode
                               binding_node_list_predicates, 
                               binding_sentence):
  ''' returns the new node, which is list of predicates clause obj after unification and resolution '''
  newnode_list_predicates = []
  for i in range(len(node_list_predicates)):
    if node_list_predicates[i] == predicate_clause_obj:
      continue
    args = node_list_predicates[i].predicate_clause.args
    new_args = []
    for j in range(len(args)):
      arg_tuple = args[j]
      if (arg_tuple[0] in binding_node_list_predicates):
        binding_tuple = binding_node_list_predicates[arg_tuple[0]]
        #if binding_tuple[1] == 'CONSTANT':
        if arg_tuple[1] == 'CONSTANT':
            print 'ERROR: can not replace constant'
            exit()
        new_args.append((binding_tuple[0],binding_tuple[1]))
      else:
        new_args.append(copy.deepcopy(arg_tuple))
    p = PredicateObj(node_list_predicates[i].predicate_clause.predicate, new_args, False)
    c = ClauseObj(None,None,None,p,node_list_predicates[i].neg)
    newnode_list_predicates.append(c)
    #Now do the same for sentence
  for i in range(len(sentence)):
    if sentence[i] == pred_in_sent:
      continue
    args = sentence[i].predicate_clause.args
    new_args = []
    for j in range(len(args)):
      arg_tuple = args[j]
      if (arg_tuple[0] in binding_sentence):
        binding_tuple = binding_sentence[arg_tuple[0]]
        #if binding_tuple[1] == 'CONSTANT':
        if arg_tuple[1] == 'CONSTANT':
            print 'ERROR: can not replace constant'
            exit()
        new_args.append((binding_tuple[0],binding_tuple[1]))
      else:
        new_args.append(copy.deepcopy(arg_tuple))
    p = PredicateObj(sentence[i].predicate_clause.predicate,new_args,False)
    c = ClauseObj(None,None,None,p,sentence[i].neg)
    newnode_list_predicates.append(c)
  return newnode_list_predicates

  '''
    temp = copy.deepcopy(node_list_predicates[i])
    args = temp.predicate_clause.args
    for i in range(len(args)):
      if binding_node_list_predicates[temp.predicate_clause.args[0]]:
        if binding_node_list_predicates[temp.predicate_clause.args[0]][1] == 'CONSTANT':
          print 'ERROR: can not replace constant'
          exit()
        temp.predicate_clause.args[0] = binding_node_list_predicates[temp.predicate_clause.args[0]][0]
        temp.predicate_clause.args[1] = binding_node_list_predicates[temp.predicate_clause.args[0]][1]
    newnode_list_predicates.append(temp)'''

def IsDuplicatePredicate(pred1_obj, pred2_obj):
  ''' Returns true both predicate match exactly '''
  if(pred1_obj.neg != pred2_obj.neg):
    return False
  if(pred1_obj.predicate_clause.predicate != pred2_obj.predicate_clause.predicate):
    return False
  args1 = pred1_obj.predicate_clause.args
  args2 = pred2_obj.predicate_clause.args
  if (len(args1) != len(args2)):
    return False
  for i in range(len(args1)):
    if(args1[i][0] != args2[i][0]):
      return False
  return True

def RemoveDuplicates(list_pred):
  freshlist = []
  if ((list_pred == None) or (len(list_pred)==0)):
    return list_pred
  if (len(list_pred) == 1):
    return list_pred
  if (len(list_pred) == 2):
    if( IsDuplicatePredicate(list_pred[0], list_pred[1]) ):
      freshlist.append(list_pred[0])
      return freshlist
    else:
      return list_pred
  else:
    #Accordint to this logic, last elem is always included
    freshlist.append(list_pred[-1])
    for i in range(len(list_pred)-1):
      found_dup = False
      for j in range(i+1, len(list_pred)):
        if(IsDuplicatePredicate(list_pred[i],list_pred[j])):
          found_dup = True
          break
      if(found_dup == False):
        freshlist.append(list_pred[i])
  return freshlist

    
def TautologyReduce(list_predicates):
  newnode_list_predicates = []
  for i in range(len(list_predicates)):
    found_opposite_predicate = False
    for j in range(len(list_predicates)):
      if i == j:
        continue
      if list_predicates[j].predicate_clause.predicate == list_predicates[i].predicate_clause.predicate:
        if list_predicates[j].neg != list_predicates[i].neg:
          args1 = list_predicates[j].predicate_clause.args 
          args2 = list_predicates[i].predicate_clause.args
          if (len(args1) == len(args2)):
            can_unify = True
            for k in range(len(args1)):
              if(args1[k][0] != args2[k][0]):
                # Every Variable and constant should match to tautology reduce.
                can_unify = False
            if(can_unify == True):
              found_opposite_predicate = True
              break
    if(found_opposite_predicate == False):
      newnode_list_predicates.append(list_predicates[i])
  freshlist = RemoveDuplicates(newnode_list_predicates)
  return freshlist


def ResolutionOrUnify(predicate_clause_obj, node_list_predicates, sentence):
  ''' 1. Returns a list i.e newnode_list_predicates after unification/resolution 
      2. The returning list will be tatutology simplified '''
  old_sentence_list = []
  GetListFromTree(sentence, old_sentence_list)
  sentence_list = []
  sentence_list = TautologyReduce(old_sentence_list)
  pred_in_sent = PredToUnify(predicate_clause_obj, sentence_list)
  if pred_in_sent == None:
    return [], False
  binding_node_list_predicates = {}
  binding_sentence = {}
  bool_val = ChangesToArgs(predicate_clause_obj, pred_in_sent, binding_node_list_predicates, binding_sentence)
  if (bool_val == False):
    return [], False
  temp_newnode_list_predicates = BuildNewnodeListPredicates(node_list_predicates, 
                                                       predicate_clause_obj, #predicate in node_list_predicates that needs to be skipped in newnode
                                                       sentence_list, 
                                                       pred_in_sent,# predicate in sentence that needs to be skipped in newnode
                                                       binding_node_list_predicates, 
                                                       binding_sentence)
  newnode_list_predicates = TautologyReduce(temp_newnode_list_predicates)
  if((len(temp_newnode_list_predicates)>1) and 
     (len(newnode_list_predicates)==0)):# means, newnode list collapsed due to tautology, meaning that the previous newnode list contradicted with the KB.
      collapsed_due_to_tauto = True
  else:
      collapsed_due_to_tauto = False
  return newnode_list_predicates , collapsed_due_to_tauto 


def CheckCommonSentence(list_list_of_sentence):
  common = []
  if (len(list_list_of_sentence) == 0):
    return set(common)
  if (len(list_list_of_sentence) == 1):
    return set(list_list_of_sentence[0])
  common_set = set(list_list_of_sentence[0])
  for s in list_list_of_sentence[1:]:
      common_set.intersection_update(s)
  return common_set
  ''' 
  repeated = set()
  visited = set()
  for item in list_list_of_sentence:
      for i in item:
          if i in visited:
            repeated.add(i)
          else:
            visited.add(i)
  return repeated'''

  '''d={}
  for x in list_list_of_sentence:
    for y in x:
        if not d.has_key(y):
          d[y]=0
        d[y]+=1
  return [x for x,y in d.iteritems() if y>1]'''


def IsOppositePred(pred_clause_obj1, pred_clause_obj2):
   ''' returns true if they are opposite '''
   if(pred_clause_obj1.predicate_clause.predicate != pred_clause_obj2.predicate_clause.predicate):
     return False
   if(pred_clause_obj1.neg == pred_clause_obj2.neg):
     return False
   args1 = pred_clause_obj1.predicate_clause.args
   args2 = pred_clause_obj2.predicate_clause.args
   if(len(args1) != len(args2)):
     return False
   for i in range(len(args1)):
     if ((args1[i][1] == 'CONSTANT') and (args2[i][1] == 'CONSTANT')):
       #TODO:What for variables??
       # I think what we are doing now is fine.
       if(args1[i][0] != args2[i][0]):
         return False
   return True

def CheckContradictionOfSentences(sent1, sentTree):
  ''' 1. Returns True :
         if Pred(const) and ~Pred(const) are there
         in sent1 and sentTree , for all the pred in sent1 
         i.e opposite of every predicate. (Note: len of both should match)
      2. Returns False: Otherwise '''
  old_sent2 = []
  GetListFromTree(sentTree, old_sent2)
  sent2 = []
  sent2 = TautologyReduce(old_sent2)
  if len(sent1) != len(sent2):
    return False
  for i in range(len(sent1)):
    found_neg = False
    for j in range(len(sent2)):
      if(IsOppositePred(sent1[i], sent2[j])):
        found_neg = True
        break
    if (found_neg == False):
      return False
  if DEBUG_ENABLE:
    debug_print('Contardicting sentence in KB:')
    PrintPredicateList(sent2)
  return True

def CheckContradictionWithKB(newnode_list_predicates, predicate_hashmap):
  ''' Returns True if Contradiction is found '''
  list_list_of_sentence = []
  for i in range(len(newnode_list_predicates)):
    if newnode_list_predicates[i].neg == True: #look up in the flip of neg
      list_of_sentence = predicate_hashmap[newnode_list_predicates[i].predicate_clause.predicate][POSITIVE]
    else:
      list_of_sentence = predicate_hashmap[newnode_list_predicates[i].predicate_clause.predicate][NEGATIVE]
    if (not(list_of_sentence in list_list_of_sentence)):
        list_list_of_sentence.append(list_of_sentence)
  common_sent_set = CheckCommonSentence(list_list_of_sentence)
  for item in common_sent_set:
    if (CheckContradictionOfSentences(newnode_list_predicates, item)):
      #Found contradiction
      return True
  return False

cache_visited = {}
# cache for predicate-->[newnode_list_predicates, newnode_list_predicates,..] i.e list of lists

def MatchingArgs(args_newnode, args_already_visited):
  if (len(args_newnode) != len(args_already_visited)):
    print'ERROR: We expect len to be same'
    exit()
  for i in range(len(args_newnode)):
    if((args_newnode[i][1]=='VARIABLE') and
       (args_already_visited[i][1]=='CONSTANT')):
      # means, conosider it as not visited
      return False
    if((args_newnode[i][1]=='CONSTANT') and 
       (args_already_visited[i][1]=='CONSTANT')):
       if(args_newnode[i][0] != args_already_visited[i][0]):
         # means, conosider it as not visited
         return False 
  # if here, means, args match with respect to node being visited 
  # i.e args match , matching the predicate
  return True

def AlreadyVisited(newnode_list_predicates):
  ''' If All the predicates in the input is visited before, 
      as a node together, i.e same predicates with same args in a node, 
      then we return True. Else we return False '''
  #TODO: 
  #We will have to do a manual compare since each newnode_list_predicates is created
  # for each new recursion. So, cannot just do trivial compare.
  global cache_visited
  list_list_of_sentence = []
  for i in range(len(newnode_list_predicates)):
    pred = newnode_list_predicates[i].predicate_clause.predicate
    if (not(pred in cache_visited)):
      return False
    if (newnode_list_predicates[i].neg):
      sentence_list = cache_visited[pred][NEGATIVE]
    else:
      sentence_list = cache_visited[pred][POSITIVE]
    if sentence_list not in list_list_of_sentence:
      list_list_of_sentence.append(sentence_list)
  if (len(list_list_of_sentence) == 0):
    return False
  sents_visited = CheckCommonSentence(list_list_of_sentence)
  if (len(sents_visited) == 0):
    return False
  for sentence in sents_visited:
    sentence_matched = True
    if (len(newnode_list_predicates) != len(sentence)):
      continue
    for i in range(len(newnode_list_predicates)):
      found_matching_pred = False
      for j in range(len(sentence)):
        if(newnode_list_predicates[i].predicate_clause.predicate == sentence[j].predicate_clause.predicate):
          if (newnode_list_predicates[i].neg == sentence[j].neg):
            if(MatchingArgs(newnode_list_predicates[i].predicate_clause.args, sentence[j].predicate_clause.args)):
              found_matching_pred = True
      if (found_matching_pred==False):
        sentence_matched = False
        break
    if (sentence_matched==True):
      return True
  #If here, means, none of the common sentences picked seem to have visited.
  return False

def UpdateCacheWithNewnodePredList(newnode_list_predicates):
  global cache_visited
  for pred_clause_obj in newnode_list_predicates:
    predicate = pred_clause_obj.predicate_clause.predicate
    if (not(predicate in cache_visited)):
        Initialize(cache_visited, predicate)
    if (pred_clause_obj.neg):
      if(not(newnode_list_predicates in cache_visited[predicate][NEGATIVE])):
          cache_visited[predicate][NEGATIVE].append(tuple(newnode_list_predicates))
    else:
      if(not(newnode_list_predicates in cache_visited[predicate][POSITIVE])):
          cache_visited[predicate][POSITIVE].append(tuple(newnode_list_predicates))

def PrintPredicate(predicate_clause_obj):
  print '%s%s:'%(('~'if predicate_clause_obj.neg else ''),predicate_clause_obj.predicate_clause.predicate), [arg[0] for arg in predicate_clause_obj.predicate_clause.args],

def PrintPredicateList(list_predicates):
  for i in range(len(list_predicates)):
    PrintPredicate(list_predicates[i])
    print '|',
  print ''

def DebugResolutionOrUnify(predicate_clause_obj, node_list_predicates, sentences, result):
  print '@@@@@@DebugResolutionOrUnify@@@@@'
  print'Unifying Predicate:'
  PrintPredicate(predicate_clause_obj)
  print'\nNode:'
  PrintPredicateList(node_list_predicates)
  print'KBSentence:'
  sentence_list = []
  GetListFromTree(sentences, sentence_list)
  PrintPredicateList(sentence_list)
  print 'Newnode:'
  PrintPredicateList(result)
  
def FindContradiction(node_list_predicates, predicate_hashmap, fd_output):
  global DEBUG_ENABLE
  for predicate_clause_obj in node_list_predicates:
    if predicate_clause_obj.neg == True: # IMP: lookup in ~Predicate (i.e flip) 
      list_of_sentences = predicate_hashmap[predicate_clause_obj.predicate_clause.predicate][POSITIVE]
    else:
      list_of_sentences = predicate_hashmap[predicate_clause_obj.predicate_clause.predicate][NEGATIVE]
    for i in range(len(list_of_sentences)):
      newnode_list_predicates, collapsed_due_to_tauto = ResolutionOrUnify(predicate_clause_obj,node_list_predicates,list_of_sentences[i])
      #Note: Bug Fix- If collapsed_due_to_tauto is True that means we could not contradict, hence move on.
      '''if collapsed_due_to_tauto:
        if DEBUG_ENABLE:
          debug_print('Collapsed due to tautology in prev node list:')
          PrintPredicateList(node_list_predicates)
        fd_output.write('TRUE\n')
        print'TRUE'
        return True'''
      if DEBUG_ENABLE:
        DebugResolutionOrUnify(predicate_clause_obj,node_list_predicates,list_of_sentences[i], newnode_list_predicates)
      if (len(newnode_list_predicates) == 0):
        continue
      if ( AlreadyVisited(newnode_list_predicates) == True):
        if DEBUG_ENABLE:
          debug_print('Loop detected for newnode_list:')
          PrintPredicateList(newnode_list_predicates)
        continue
      UpdateCacheWithNewnodePredList(newnode_list_predicates)
      if(len(newnode_list_predicates) == 1): 
        #Note: If a list with more than 1 predicate is in contradiction with the kB, it will be detected in collapsed_due_to_tauto in next loop.
        if (CheckContradictionWithKB(newnode_list_predicates,predicate_hashmap) == True):
          fd_output.write('TRUE\n')
          print'TRUE'
          return True
      #if ( AlreadyVisited(newnode_list_predicates) == True):
      #  return False
      if(FindContradiction(newnode_list_predicates,predicate_hashmap,fd_output) == True):
        return True
  return False 

def RemoveTheAddedQueryFromKB(neg_query_clause_obj, KB_sentences_list, predicate_hashmap):
  #remove from the hashmap first 
  value = predicate_hashmap[neg_query_clause_obj.predicate_clause.predicate]
  if (neg_query_clause_obj.neg == True):
    last_added_elem = value[NEGATIVE].pop()
  else:
    last_added_elem = value[POSITIVE].pop()
  if last_added_elem != neg_query_clause_obj: #double checking
    print 'ERROR: We expect last_added_elem to be same as previously added obj, neg_query_clause_obj'
    exit()
  #remove from the KB
  popped_elem = KB_sentences_list.pop()
  if popped_elem != neg_query_clause_obj: #double checking
    print 'ERROR: We expect popped_elem to be same as previously added obj, neg_query_clause_obj'
    exit()

def InspectQuery(query_clause_obj,
                 KB_sentences_list,
                 predicate_hashmap,
                 fd_output
                ):
  global cache_visited
  cache_visited = {}
  neg_query_clause_obj = CreateNegQuery(query_clause_obj)
  AddQueryToKB(neg_query_clause_obj, KB_sentences_list, predicate_hashmap)
  node_list_predicates = []
  node_list_predicates.append(neg_query_clause_obj)
  UpdateCacheWithNewnodePredList(node_list_predicates)
  # First check if the given query is already in contradiction with the KB
  if (CheckContradictionWithKB(node_list_predicates,predicate_hashmap) == True):
    fd_output.write('TRUE\n')
    print'TRUE'
    RemoveTheAddedQueryFromKB(neg_query_clause_obj, KB_sentences_list, predicate_hashmap)
    return 
  #Start the DFS search to try to prove the contradiction
  outcome = FindContradiction(node_list_predicates, predicate_hashmap, fd_output)
  if (outcome == False):
    print 'FALSE'
    fd_output.write('FALSE\n')
  RemoveTheAddedQueryFromKB(neg_query_clause_obj, KB_sentences_list, predicate_hashmap)

def StandardizeArgs(args):
  global STANDARDIZE_KB_COUNT
  new_args = []
  for i in range(len(args)):
    arg_tuple = args[i]
    if arg_tuple[1] == 'VARIABLE':
      new_variable = '%s'%(arg_tuple[0])+'%d'%(STANDARDIZE_KB_COUNT)
      new_args.append((new_variable.strip(),'VARIABLE'))
    else:
      new_args.append(arg_tuple)
  return new_args

def StandardizeVariables(root):
  if root == None:
    return
  elif(root.operator == None):
    if(root.predicate_clause != None):
      root.predicate_clause.args = StandardizeArgs(root.predicate_clause.args)
      return
    else:
      print'Error:Leaf node should be having predicate clause'
      exit()
  else:
    #If here means, root op is not None
    StandardizeVariables(root.left_clause)
    StandardizeVariables(root.right_clause)

def main():
  global SETTLED_DOWN
  global DEBUG_ENABLE
  global STANDARDIZE_KB_COUNT
  _input = _Input()
  ParseInputFile(_input)
  if DEBUG_ENABLE:
    DisplayQueryList(_input)
    DisplaySentLineList(_input)
  KB_sentences_list = []
  global given_sentences_root
  for i in range(_input.total_sent_lines):
        debug_print('\n\n----------------------------')
        debug_print('Given Sentence%d: %s'%(i,_input.sent_lines_list[i]))
        root = yacc.parse(_input.sent_lines_list[i])
        #from pprint import pprint
        #pprint (vars(result))
        MoveNegDownTheTree(root)
        debug_print('----------------------------')
        debug_print('Before Distributing | over &')
        DisplayTree(root)
        #print'----------------------------'
        SETTLED_DOWN = False
        while (SETTLED_DOWN == False):
          SETTLED_DOWN = True
          ConvertToCNF(root)
        debug_print('----------------------------')
        debug_print('After Distributing | over &')
        DisplayTree(root)
        #print'----------------------------'
        #RoughDisplaySentences(root)
        BuildSentences(root,KB_sentences_list)
        given_sentences_root.append(root)
  for i in range(len(KB_sentences_list)):
    StandardizeVariables(KB_sentences_list[i])
    STANDARDIZE_KB_COUNT = (STANDARDIZE_KB_COUNT + 1)
  debug_print('*****************************')
  debug_print('KB Sentences:')
  for i in range(len(KB_sentences_list)):
    DisplayTree(KB_sentences_list[i])
  debug_print('*****************************')
  predicate_hashmap = {}
  BuildHashMapOfPredicates(predicate_hashmap, KB_sentences_list)
  #pprint.pprint(predicate_hashmap)
  fd_output = open('output.txt', 'w')
  for i in range(_input.total_queries):
    print'query%d:%s'%(i,_input.query_list[i].predicate_clause.predicate), _input.query_list[i].predicate_clause.args
    InspectQuery(_input.query_list[i], 
                 KB_sentences_list,
                 predicate_hashmap,
                 fd_output)

  fd_output.close()


if __name__ == '__main__':
  main()

