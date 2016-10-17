#!/usr/bin/env python

import os
import subprocess
from os import listdir
from subprocess import call

directories = ('depth1',)
errors = []

def main():
  global errors
  for i in range(1,5):
    os.system('rm -rf depth%d_out'%i)
    os.system('rm -rf depth%derrors.txt'%i)
    os.system('mkdir depth%d_out'%i)
  
  for directory in directories:
    os.system('rm -rf %s.errors.txt'%directory)
    errors = []
    files = os.listdir(directory)
    filecount = 0
    for filename in files:
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
      outputfilename = int(filter(str.isdigit, '%s'%filename))
      print 'mv output.txt %s_out/%s.out'%(directory,outputfilename)
      try:
        out = os.system('cp output.txt %s_out/%s.out'%(directory,outputfilename)).read()
        if 'No such file or directory' in out:
          print 'Error' 
          exit()
      except: 
        pass
      fd1 = open('output.txt','rU')
      lines1 = fd1.read()
      fd2 = open('./OUTPUT/%s.out'%outputfilename,'rU')
      lines2 = fd2.read()
      if (lines1 != lines2):
        errors.append('%s'%filename)
      filecount += 1
    fderrors = open('%s.errors.txt'%directory,'w')
    fderrors.write('TotalFiles=%d;Errorslen=%d\n'%(filecount, len(errors)))
    for item in errors:
      fderrors.write(item)
    fderrors.write('\n')
    print '//////////////////////////'
    print '////////DONE///////////////'
    print 'Errors:',errors

if __name__ == '__main__':
  main()
