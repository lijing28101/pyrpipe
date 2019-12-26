#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 15:56:20 2019

@author: usingh
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 16:24:44 2019

@author: usingh
"""
import pytest
from pyrpipe import sra
from testingEnvironment import testSpecs
import os

testVars=testSpecs()

def test_assembly():
    srrID=testVars.srr
    print ("Testing Assembly...")
    testDir=testVars.testDir
    newOb=sra.SRA(srrID,testDir)
    assert newOb.getSrrAccession()==srrID,"Failed SRA init"
    assert newOb.downloadSRAFile()==True, "Failed to download SRA file"
    assert newOb.sraFileExistsLocally()==True, "Failed to locate .sra file on disk"
    ##test fasterq-dump
    assert newOb.runFasterQDump(deleteSRA=True,**{"-f":"","-t":testDir})==True, "Failed FQ dump"
    assert newOb.fastqFilesExistsLocally()==True, "Failed to locate .fastq files on disk"
    assert newOb.sraFileExistsLocally()!=True, "Failed to delete .sra files from disk"
    