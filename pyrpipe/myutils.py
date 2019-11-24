#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 12:04:28 2019

@author: usingh
"""

import os
import subprocess

#functions to print in color

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def printBoldRed(text):
    print (bcolors.FAIL + bcolors.BOLD+ text + bcolors.ENDC)

def printGreen(text):
    print (bcolors.OKGREEN + text + bcolors.ENDC)

def printBlue(text):
    print (bcolors.OKBLUE + text + bcolors.ENDC) 

######End color functions###################

def getCommandReturnValue(cmd):
    result = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    stdout,stderr = result.communicate()
    return result.returncode

def executeCommand(cmd):
      
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
            yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)
        

def getSRADownloadPath(srrID):
    if len(srrID) <6:
        return None
    
    parentPath="anonftp@ftp.ncbi.nlm.nih.gov:/sra/sra-instant/reads/ByRun/sra/"
    parentPath=parentPath+srrID[0:3]+"/"+srrID[0:6]+"/"+srrID+"/"+srrID+".sra"
    
    return parentPath
    
#function to search files using find and return results as a list
def findFiles(path,name,recursive):
    if recursive:
        find_cmd=['find', path,'-type', 'f','-name',name]   
    else:
        find_cmd=['find', path,'-type', 'f','-maxdepth', '1','-name',name] 
    print ("Executing: "+ ' '.join(find_cmd))
    #get output as string
    out = subprocess.check_output(find_cmd,universal_newlines=True)
    results=out.split()
    return results

def checkPathsExists(*args):
    failFlag=False
    for path in args:
        if not os.path.exists(path):
            printBoldRed("Path not found: "+path)
            failFlag=True
    if failFlag==True:
        return False
    return True


def checkFilesExists(*args):
    failFlag=False
    for path in args:
        if not os.path.isfile(path):
            printBoldRed("File not found: "+path)
            failFlag=True
    
    if failFlag:
        return False
    return True

def checkHisatIndex(index):
    return checkFilesExists(index+".1.ht2")
    

def bytetoReadable(sizeInBytes):
    """
    function to convert bytes to human readable format (MB,GB ...)
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if sizeInBytes < 1024.0:
            return "%3.1f %s" % (sizeInBytes, x)
        sizeInBytes /= 1024.0


def getFileSize(file_path):
    """
    Return File size in human readable format
    """
    
    if (checkFilesExists(file_path)):
        file_info = os.stat(file_path)
        return bytetoReadable(file_info.st_size)
    
def parseUnixStyleArgs(validArgsList,passedArgs):
    """
    Function creates arguments to pass to unix systems through popen
    Parameters
    ----------
    arg1 : list
        list of valid arguments. Invalid arguments will be ignored
    arg2: keyword value argument list to be parsed
        
    Returns
    -------
        list
            a list with command line arguments to be used with popen

        Examples
        --------
        >>> parseUnixStyleArgs(['-O','-t','-q'], **{"-O": "./test", "Attr2": "XX","-q":""})
        ['-O','./test','-q']
    """
    popenArgs=[]
    for key, value in passedArgs.items():
        #check if key is a valid argument
        if key in validArgsList:
            popenArgs.append(key)
            #do not add emty parameters e.g. -q or -v
            if len(value)>0:
                    popenArgs.append(value)
        else:
            print("Unknown argument {0} = {1}. ignoring...".format(key, value))
    return popenArgs
    
    

if __name__ == "__main__":
    #test
    #print(getSRADownloadPath('SRR002328'))
    print(findFiles("/home/usingh/work/urmi","*.py",False))
 

    
