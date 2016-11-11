#! /usr/bin/env python

import sys
import ply.lex as lex
import re

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

# Give the lexer some input
lexer.input(data)

# Tokenize
while True:
    tok = lexer.token()
    if not tok: 
        break      # No more input
    #print(tok)
    from pprint import pprint
    print'--------------------'
    try:
      pprint (vars(tok.value))
    except:
      print(tok)
      pass
