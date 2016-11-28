#!/usr/bin/env python

import os
import subprocess
from os import listdir
from subprocess import call
import filecmp
import shutil

tmpDirectory = ('tmpInput',)
MasterInputDir = 'MasterInput'
MasterOutputDirectory = 'MasterOutput'
OutputFile = 'output.txt'
#directories = ('BACKUP_BFS',)

import errno

COUNT = 0
 
def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)

def mov(directory,filename):
      print 'mv output.txt %s/%s.output'%(directory,filename)
      try:
        out = os.system('mv output.txt %s/%s.output'%(directory,filename)).read()
        if 'No such file or directory' in out:
          print 'Error'
          exit()
      except:
        pass


def CompareOutputWithMasterOutput(directory, filename):
  global MasterOutputDirectory
  global OutputFile
  print 'Comparing output.txt and %s/%s.output'%(MasterOutputDirectory,filename)
  bool_val = filecmp.cmp('%s'%OutputFile, '%s/%s.output'%(MasterOutputDirectory,filename))
  if bool_val == False:
    print'output of %s did not match the masteroutput'%filename
    print '!!!!! TEST CASE FAILED !!!!!'
    mov(directory,filename)
    exit()


def main():
  print '******************************************************************************************'
  print'COPING ALL FILES IN %s/ TO %s/'%(MasterInputDir, tmpDirectory[0])
  copy('%s'%MasterInputDir,'%s'%tmpDirectory[0])
  for directory in tmpDirectory:
    files = os.listdir(directory)
    for filename in files:
      if 'output' in filename:
        continue
      print '------------------------------------------------------------------------------------------'
      exe = 'cp ./%s/%s ./input.txt'%(directory,filename)
      print exe
      os.system(exe)
      try:
        print './homework.py'
        os.system('./homework.py')
        global COUNT
        COUNT = COUNT +1
      except:
        print 'Error in executing %s'%filename
        exit()
      CompareOutputWithMasterOutput(directory,filename)
      print 'TEST CASE PASSED!'
      mov(directory,filename)
      '''
      print 'mv output.txt %s/%s.output'%(directory,filename)
      try:
        out = os.system('mv output.txt %s/%s.output'%(directory,filename)).read()
        if 'No such file or directory' in out:
          print 'Error' 
          exit()
      except: 
        pass'''

if __name__ == '__main__':
  main()
  print 'Total TestCases = %d'%COUNT
