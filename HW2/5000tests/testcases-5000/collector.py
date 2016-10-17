#! /usr/bin/env python

import os
import subprocess
from os import listdir
from subprocess import call

START_FILE = 1
END_FILE = 5000

def main():
  try:
    os.system('rm -rf ./depth1')
    os.system('rm -rf ./depth2')
    os.system('rm -rf ./depth3')
    os.system('rm -rf ./depth4')
    os.system('mkdir ./depth1')
    os.system('mkdir ./depth2')
    os.system('mkdir ./depth3')
    os.system('mkdir ./depth4')
  except:
    pass
  for i in range(START_FILE, END_FILE):
    fd = open('./INPUT/%d.in'%i, 'r')
    lines = fd.read().split('\n')
    depth = int(lines[3])
    if depth==1:
      exe = 'cp ./INPUT/%d.in ./depth1/%d.in'%(i,i)
      os.system(exe)
    elif depth == 2:
      exe = 'cp ./INPUT/%d.in ./depth2/%d.in'%(i,i)
      os.system(exe)
    elif depth == 3:
      exe = 'cp ./INPUT/%d.in ./depth3/%d.in'%(i,i)
      os.system(exe)
    elif depth == 4:
      exe = 'cp ./INPUT/%d.in ./depth4/%d.in'%(i,i)
      os.system(exe)
    fd.close()

if __name__ == '__main__':
  main()
