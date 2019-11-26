#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 17:48:00 2019

@author: usingh
"""

from myutils import *

class RNASeqQC:
    def __init__(self):
        self.category="RNASeqQC"

class Trimgalore(RNASeqQC):
    def __init__(self,**kwargs):
        """
        Parameters
        ----------
        kwargs:
            trim_galore arguments. could override later too.
        """
        
        #run super to inherit parent class properties
        super().__init__() 
        self.programName="trim_galore"
        self.depList=[self.programName,'cutadapt']
        self.validArgsList=['-h','-v','-q','--phred33','--phred64','--fastqc','--fastqc_args','-a','-a2',
                            '--illumina','--nextera','--small_rna','--consider_already_trimmed',
                            '--max_length','--stringency','-e','--gzip','--dont_gzip','--length',
                            '--max_n','--trim-n','-o','--no_report_file','--suppress_warn',
                            '--clip_R1','--clip_R2','--three_prime_clip_R1','--three_prime_clip_R2',
                            '--2colour','--path_to_cutadapt','--basename','-j','--hardtrim5','--hardtrim3',
                            '--clock','--polyA','--rrbs','--non_directional','--keep','--paired','-t',
                            '--retain_unpaired','-r1','-r2']
        #check if hisat2 exists
        if not checkDep(self.depList):
            raise Exception("ERROR: "+ self.programName+" not found.")
            
        #initialize the passed arguments
        self.passedArgumentList=parseUnixStyleArgs(self.validArgsList,kwargs)
        print(self.passedArgumentList)
        
            
    def run(self,sraOb):
        """Run this class' program.
        The function run() is consistent for all QC classess.
        This function returns a tuple containing the status and the file paths to the qc-corrected fastq files (in order 1,2 for paired)
        """
        return self.runTrimGalore(sraOb)
            
            
    def runTrimGalore(self,sraOb):
        #get layout
        if sraOb.layout=='PAIRED':
            fq1=sraOb.localfastq1Path
            fq2=sraOb.localfastq2Path
            return self.runTrimGalorePaired(fq1,fq2)
        else:
            return self.runTrimGaloreSingle(sraOb.localfastqPath)
            
        
            
    def runTrimGaloreSingle(self,fastqFilePath):
        print("Running trim_galore unpaired")
        
        trimGaloreCmd=['trim_galore']
        #check if out dir is specified
        if '-o' not in self.passedArgumentList:            
            #default output dir
            outDir=os.path.split(fastqFilePath)[0]
            trimGaloreCmd.extend(['-o',outDir])
        trimGaloreCmd.extend(self.passedArgumentList)
        trimGaloreCmd.extend([fastqFilePath])

        print("Executing: "+" ".join(trimGaloreCmd))
        try:
            for output in executeCommand(trimGaloreCmd):
                print (output)
        except subprocess.CalledProcessError as e:
            print ("Error in command")
            return False
        
        print("Exiting...")
        return True
        
            
    def runTrimGalorePaired(self,fastqFile1Path,fastqFile2Path):
        print ("Running trim_galore paired")
        
        trimGaloreCmd=['trim_galore']
        #check if out dir is specified
        if '-o' not in self.passedArgumentList:            
            #default output dir
            outDir=os.path.split(fastqFile1Path)[0]
            trimGaloreCmd.extend(['-o',outDir])
        trimGaloreCmd.extend(self.passedArgumentList)
        trimGaloreCmd.extend(['--paired',fastqFile1Path,fastqFile2Path])
        print("Executing: "+" ".join(trimGaloreCmd))
        try:
            for output in executeCommand(trimGaloreCmd):
                print (output)
        except subprocess.CalledProcessError as e:
            print ("Error in command")
            return False
        
        print("Exiting...")
        return True
            
            

class BBmap(RNASeqQC):
    def __init__(self):
        """
        Parameters
        ----------
        kwargs:
            bbduk.sh arguments. could override later too.
        """
        #run super to inherit parent class properties
        super().__init__() 
        self.programName="bbduk.sh"
        self.depList=[self.programName]
        #note that bbduk.sh argument style is different that other linux commands
        self.validArgsList=[]
        #check if hisat2 exists
        if not checkDep(self.depList):
            raise Exception("ERROR: "+ self.programName+" not found.")
            
    def run(self,sraOb):
        """Execeute the QC method 
        """
        if sraOb.layout=='PAIRED':
            fq1=sraOb.localfastq1Path
            fq2=sraOb.localfastq2Path
            return self.runBBdukPaired(fq1,fq2,"/home/usingh/lib_urmi/softwares/bbmap/resources/adapters.fa")
        else:
            return self.runBBdukSingle(sraOb.localfastqPath)
    
    def runBBdukSingle(self):
        print ("Running bbduk single")
        
            
    def runBBdukPaired(self,fastqFile1Path,fastqFile2Path,pathToAdapters="",proc="auto",ktrim='r',k=23,mink=11,hdist=1,qtrim='rl',trimq=10):
        """Function to run BBduk on paired data
        """
        print ("Running bbduk paired")
        
        #default output dir
        outDir=os.path.split(fastqFile1Path)[0]
        outFileName1=os.path.split(fastqFile1Path)[1].split(".fastq")[0]+"_1_bbduk.fastq"
        outFileName2=os.path.split(fastqFile2Path)[1].split(".fastq")[0]+"_1_bbduk.fastq"
        outFile1=os.path.join(outDir,outFileName1)
        outFile2=os.path.join(outDir,outFileName2)
        
        bbdukCmd=['bbduk.sh','-Xmx1g','in1='+fastqFile1Path,'in2='+fastqFile2Path,'out1='+outFile1,'out2='+outFile2,'ref='+pathToAdapters,'ktrim='+ktrim,'k='+str(k),'mink='+str(mink),'hdist='+str(hdist),'qtrim='+qtrim,'trimq='+str(trimq),'threads='+str(proc)]
        print("Executing: "+" ".join(bbdukCmd))
        
        
        try:
                for output in executeCommand(bbdukCmd):
                    print (output)
        except subprocess.CalledProcessError as e:
                print ("Error in command")
                return False
        print("Exiting...")
        
        #check if file exists
        if not checkFilesExists(outFile1,outFile2):
            print ("ERROR in running"+ self.programName)
            return False,"NA","NA"
        
        return True,outFile1,outFile2