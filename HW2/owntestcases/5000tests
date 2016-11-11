#!/usr/bin/env python

import os
import subprocess
from os import listdir
from subprocess import call

directories = ('BFS', 'DFS', 'UCS', 'ASTAR', 'Avi/1', 'Avi/2')
#directories = ('BACKUP_BFS',)

def main():
  for directory in directories:
    files = os.listdir(directory)
    for filename in files:
      if 'output' in filename:
        continue
      print '------------------------'
      exe = 'cp ./%s/%s ./input.txt'%(directory,filename)
      print exe
      os.system(exe)
      try:
        print './homework.py'
        os.system('./homework.py')
      except:
        print 'Error in executing %s'%filename
        exit()
      print 'mv output.txt %s/%s.output'%(directory,filename)
      try:
        out = os.system('mv output.txt %s/%s.output'%(directory,filename)).read()
        if 'No such file or directory' in out:
          print 'Error' 
          exit()
      except: 
        pass

if __name__ == '__main__':
  main()
