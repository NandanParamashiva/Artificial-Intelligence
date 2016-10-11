#! /usr/bin/env python

from collections import deque

class person(object):
  def __init__(self):
    self.name = None
    self.age = 0

  def setvalues(self, name, age):
    self.name = name
    self.age = age

#def mod(p1,p2):

def main():
  print 'main test'
  p1 = person()
  p1.setvalues('alex',10)
  p2 = person()
  p2.setvalues('vargese',20)

  maths = []
  social = []
  #section = []
  section = deque()
  section.append(p1)
  section.append(p2)
  maths.append(p1)
  maths.append(p2)
  social.append(p1)
  social.append(p2)
  print 'section=',section,len(section)
  #print 'maths=',maths,len(maths)
  #print 'social=',social,len(social)
  print 'first elem',section[0].name,section[0].age
  print 'sec elem',section[1].name,section[1].age
  print p1.name,p1.age
  print p2.name,p2.age
  section.popleft()
  print 'after popleft'
  print 'first elem',section[0].name,section[0].age
  print 'section=',section,len(section)
  #print 'maths=',maths,len(maths)
  #print 'social=',social,len(social)


if __name__ == '__main__':
  main()
