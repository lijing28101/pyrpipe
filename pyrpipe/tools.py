#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 14:54:22 2019

@author: usingh
"""
from pyrpipe import pyrpipe_utils as pu
from pyrpipe import pyrpipe_engine as pe
import os

class RNASeqTools:
    def __init__(self):
        self.category="RNASeqTools"
    

class Samtools(RNASeqTools):
    def __init__(self,**kwargs):
        self.programName="samtools"
        #check if hisat2 exists
        if not pe.check_dependencies([self.programName]):
            raise Exception("ERROR: "+ self.programName+" not found.")
        
        self.valid_args=['-b','-C','-1','-u','-h','-H','-c','-o','-U','-t','-L','-r',
                            '-R','-q','-l','-m','-f','-F','-G','-s','-M','-x','-B','-?','-S','-O','-T','-@']
        
        self.passedArgumentDict=kwargs
        
        
        
    def sam_to_bam(self,sam_file,out_dir="",out_suffix="",delete_sam=False,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Convert sam file to a bam file. 
        Output bam file will have same name as input sam.
        
        out_suffix: string
            Suffix for the output sam file
        delete_sam(bool): delete the sam file after conversion
        verbose (bool): Print stdout and std error
        quiet (bool): Print nothing
        logs (bool): Log this command to pyrpipe logs
        objectid (str): Provide an id to attach with this command e.g. the SRR accession. This is useful for debugging, benchmarking and reports.
        kwargs (dict): Options to pass to trimgalore. This will override the existing options 
        
        Returns
        -------
        string
                Returns the path to the bam file. Returns empty string if operation failed.
        """        
        if not out_dir:            
            out_dir=pu.get_file_directory(sam_file)
        else:
            if not pu.check_paths_exist(out_dir):
                pu.mkdir(out_dir)
        
        fname=pu.get_file_basename(sam_file)
        
        #output will be out_bam
        out_bam=os.path.join(out_dir,fname+out_suffix+'.bam')
        
        newOpts={"--":(sam_file,),"-o":out_bam,"-b":""}
        mergedOpts={**kwargs,**newOpts}
        
        status=self.run_samtools("view",verbose=verbose,quiet=quiet,logs=logs,objectid=objectid,**mergedOpts)
                
        if not status:
            print("Sam to bam failed for:"+sam_file)
            return ""
        
        #check if bam file exists
        if not pu.check_files_exist(out_bam):
            return ""
        
        #delete_sam_file
        if delete_sam:
            if not pe.deleteFileFromDisk(sam_file):
                print("Error deleting sam file:"+sam_file)
                
        #return path to file
        return out_bam
        
        
        
        
    #sort bam file.output will be bam_file_sorted.bam
    def sort_bam(self,bam_file,out_dir="",out_suffix="",delete_bam=False,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Sorts an input bam file. Outpufile will end in _sorted.bam
        
        verbose (bool): Print stdout and std error
        quiet (bool): Print nothing
        logs (bool): Log this command to pyrpipe logs
        objectid (str): Provide an id to attach with this command e.g. the SRR accession. This is useful for debugging, benchmarking and reports.
        kwargs (dict): Options to pass to trimgalore. This will override the existing options 
        
        Returns
        -------
        string
                Returns path to the sorted bam file. Returns empty string if operation failed.
        
        """
        if not out_dir:
            out_dir=pu.get_file_directory(bam_file)
        else:
            if not pu.check_paths_exist(out_dir):
                pu.mkdir(out_dir)
                
        fname=pu.get_file_basename(bam_file)
        #output will be out_bam
        outSortedbam_file=os.path.join(out_dir,fname+out_suffix+'_sorted.bam')
        
        newOpts={"--":(bam_file,),"-o":outSortedbam_file}
        mergedOpts={**kwargs,**newOpts}
        
        status=self.run_samtools("sort",verbose=verbose,quiet=quiet,logs=logs,objectid=objectid,**mergedOpts)
        
        if not status:
            print("Bam sort failed for:"+bam_file)
            return ""
        
        #check if bam file exists
        if not pu.check_files_exist(outSortedbam_file):
            return ""

        if delete_bam:
            if not pe.deleteFileFromDisk(bam_file):
                print("Error deleting sam file:"+bam_file)
                
        #return path to file
        return outSortedbam_file
    
    def sam_sorted_bam(self,sam_file,out_dir="",out_suffix="",delete_sam=False,delete_bam=False,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Convert sam file to bam and sort the bam file.
        verbose (bool): Print stdout and std error
        quiet (bool): Print nothing
        logs (bool): Log this command to pyrpipe logs
        objectid (str): Provide an id to attach with this command e.g. the SRR accession. This is useful for debugging, benchmarking and reports.
        kwargs (dict): Options to pass to trimgalore. This will override the existing options 
        
        Returns
        -------
        string
                Returns path to the sorted bam file. Returns empty string if operation failed.
        """
        
        sam2bam_file=self.sam_to_bam(sam_file,delete_sam=delete_sam,verbose=verbose,quiet=quiet,logs=logs,objectid=objectid,**kwargs)
        
        if not sam2bam_file:
            return ""
            

        bamSorted=self.sort_bam(sam2bam_file,out_dir=out_dir, out_suffix,delete_bam,verbose=verbose,quiet=quiet,logs=logs,objectid=objectid,**kwargs)
        
        if not bamSorted:
            return ""
        
        return bamSorted
    
    
    def merge_bam(self,*args,out_file="merged",out_dir="",delete_bams=False,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Merge multiple bam files into a single file
        
        Parameters
        ----------
        out_file: string
            Output file name to save the results. .bam will be added at the end.
        args:tuple
            Paths to bam files to combine
        out_dir: string
            Path where to save the merged bam file. Default path is the same as the first bam_file's
        verbose (bool): Print stdout and std error
        quiet (bool): Print nothing
        logs (bool): Log this command to pyrpipe logs
        objectid (str): Provide an id to attach with this command e.g. the SRR accession. This is useful for debugging, benchmarking and reports.
        kwargs (dict): Options to pass to trimgalore. This will override the existing options 
        
        kwargs: dict
            arguments passed to samtools merge command
            
        Returns
        -------
        string
            Returns the path to the merged bam file.
        """
        
        if len(args) < 2:
            print("Please supply at least 2 files to merge")
            return ""
        
        if not out_dir:
            out_dir=pu.get_file_directory(args[0])
        else:
            if not pu.check_paths_exist(out_dir):
                pu.mkdir(out_dir)
        
        outMergedFile=os.path.join(out_dir,out_file+".bam")
        
        newOpts={"--":(outMergedFile,)+args}
        
        mergedOpts={**kwargs,**newOpts}
        
        status=self.run_samtools("merge",verbose=verbose,quiet=quiet,logs=logs,objectid=objectid,**mergedOpts)
        
        if not status:
            print("Bam merge failed for:"+outMergedFile)
            return ""
        
        #check if bam file exists
        if not check_files_exist(outMergedFile):
            return ""
        

        if delete_bams:
            for bam_file in args:
                if not deleteFileFromDisk(bam_file):
                    print("Error deleting sam file:"+bam_file)
                    
        return outMergedFile
        
        
        
    def run_samtools(self,sub_command,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """A wrapper to run samtools.
        
        Parameters
        ----------
        sub_command: string
            sub_command to pass to samtools e.g. sort, merge etc
        arg1: dict
            arguments to pass to samtools. This will override parametrs already existing in the self.passedArgumentDict list but NOT replace them.
        verbose (bool): Print stdout and std error
        quiet (bool): Print nothing
        logs (bool): Log this command to pyrpipe logs
        objectid (str): Provide an id to attach with this command e.g. the SRR accession. This is useful for debugging, benchmarking and reports.
        kwargs (dict): Options to pass to trimgalore. This will override the existing options 
        
        Returns
        -------
        bool:
                Returns the status of samtools. True is passed, False if failed.
        """
            
        #override existing arguments
        mergedArgsDict={**self.passedArgumentDict,**kwargs}
       
        samtools_cmd=['samtools',sub_command]
        #add options
        samtools_cmd.extend(pu.parse_unix_args(self.valid_args,mergedArgsDict))
                
        #start ececution
        status=pe.execute_command(samtools_cmd,verbose=verbose,quiet=quiet,logs=logs,objectid=objectid)
        if not status:
            pu.print_boldred("samtools failed")
        
        #return status
        return status
        
        
        
        
        
class Portcullis(RNASeqTools):
    def __init__(self,**kwargs):
        self.programName="portcullis"
        self.depList=[self.programName]
        #check if program exists
        if not check_dependencies(self.depList):
            raise Exception("ERROR: "+ self.programName+" not found.")
        
        self.valid_args=['-t','--threads','-v','--verbose','--help','-o','-b',
                            '--bam_filter','--exon_gff','--intron_gff','--source',
                            '--force','--copy','--use_csi','--orientation','--strandedness',
                            '--separate','--extra','-r','--max_length','--canonical','--min_cov',
                            '--save_bad']
        
        self.passedArgumentDict=kwargs
        
        
    def runPortcullisFull(self,referenceFasta,bam_file,out_dir="",delete_bam_file=False,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """
        run portculis full
        
        Parameters
        ----------
        referenceFasta: string
            Path to the reference fasta file
        bam_file: string
            Path to input bam file
        out_dir: string
            Path to the out put dir. current directory is not given.
        """
        
        if not check_files_exist(referenceFasta,bam_file):
            print ("Please check input for portcullis.")
            return ""
        
        
        newOpts={"--":(referenceFasta,bam_file)}
        mergedOpts={**kwargs,**newOpts}
        #add out dir path
        if not out_dir:
            out_dir=os.path.join(os.getcwd(),"portcullis_out")
                  
        mergedOpts={**mergedOpts,**{"-o":out_dir}}
        
        status=self.runPortcullis("full",verbose=verbose,quiet=quiet,logs=logs,objectid=objectid,**mergedOpts)
        
        if not status:
            print("portcullis full failed for:"+bam_file)
            return ""
        
        #check if bam file exists
        if not checkPathsExists(out_dir):
            return ""

        if delete_bam_file:
            if not deleteFileFromDisk(bam_file):
                    print("Error deleting bam file:"+bam_file)
        
        return out_dir
    
    def runPortcullis(self,sub_command,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """
        Wrapper to run portcullis.
        
        Parameters
        ----------
         sub_command: string
            sub_command to pass to portcullis e.g. full, prep, junc etc.
        arg1: dict
            arguments to pass to samtools. This will override parametrs already existing in the self.passedArgumentDict list but NOT replace them.
            
        Returns
        -------
        bool:
                Returns the status of portcullis. True is passed, False if failed.
        """
        
        
        #override existing arguments
        mergedArgsDict={**self.passedArgumentDict,**kwargs}
       
        portcullis_Cmd=['portcullis',sub_command]
        #add options
        portcullis_Cmd.extend(parse_unix_args(self.valid_args,mergedArgsDict))
                
        print("Executing:"+" ".join(portcullis_Cmd))
        
        
        #start ececution
        status=executeCommand(portcullis_Cmd,verbose=verbose,quiet=quiet,logs=logs,objectid=objectid)
        if not status:
            print_boldred("portcullis failed")
                
        #return status
        return status
        
        
        

class Mikado(RNASeqTools):
    def __init__(self,**kwargs):
        self.programName="mikado"
        self.depList=[self.programName]
        #check if program exists
        if not check_dependencies(self.depList):
            raise Exception("ERROR: "+ self.programName+" not found.")
        
        self.valid_args=[]        
        self.passedArgumentDict=kwargs
        
        
    #mikado prepare --start-method spawn --log mikadoPrepareLog --minimum_length 30
    #--procs 28 --output-dir mikadoPrepOutNew 
    #--fasta /pylon5/mc5pl7p/usingh/lib/hisatIndex/ensembl_release98/Homo_sapiens.GRCh38.dna.primary_assembly.fa 
    #--list smolGtfList
    
    def searchGTFtolist(self, out_file,searchPath=os.getcwd(),searchQuery="*.gtf",out_dir=os.getcwd(),strand=False):
        searchCmd=['find',searchPath,'-name',searchQuery]
        st=runLinuxCommand(searchCmd)
        if st[0]==0:
            output=st[1].decode("utf-8").split("\n")
            
        return self.createMikadoGTFlist(out_file,*output,out_dir=out_dir,strand=strand)


        
    
    def createMikadoGTFlist(self,out_file,*args,out_dir=os.getcwd(),strand=False):
        """Create a file to be used by mikado configure
        """
        
        outFilePath=os.path.join(out_dir,out_file+".yaml")
        
        
        gtfs=[]
        for l in args:
            thisName=pu.get_file_basename(l)
            if thisName:
			    #print("\t".join([l,thisName,strand]))
                gtfs.append("\t".join([l,thisName,str(strand)]))
        
        f=open(outFilePath,"w")
        f.write("\n".join(gtfs))
        f.close()
        
        print_green("Mikado list file written to:"+outFilePath)
        return outFilePath
                

        
    def runMikadoFull(self):
        """Run whole mikado pipeline
        """
        pass
    
    def runMikadoConfigure(self,listFile,genome,mode,scoring,junctions,out_file,out_dir=os.getcwd(),verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Wrapper to run mikado configure
        Make sure the paths in list file are global.
        Parameters
        ----------
        
        returns
        -------
        string
            Path to the created configuration file
        """
        
        #check all file exists
        if not check_files_exist(listFile,genome,junctions,scoring):
            print("Please check mikado input")
            return ""
        
        #create out dir
        if not checkPathsExists(out_dir):
            if not mkdir(out_dir):
                raise Exception("Exception in mikado configure.")
            
        outFilePath=os.path.join(out_dir,out_file+".yaml")
        
        newOpts={"--list":listFile,"--reference":genome,"--mode":mode,"--scoring":scoring,"--junctions":junctions,"--":(outFilePath,)}
        
        #merge with kwargs
        mergedOpts={**kwargs,**newOpts}
        
        status=self.runMikado("configure",verbose=verbose,quiet=quiet,logs=logs,objectid=objectid,**mergedOpts)
        
        if not status:
            print_boldred("Mikado configure failed.\nPlease make sure the paths in list file are global.")
            return ""
        
        #check if bam file exists
        if not check_files_exist(outFilePath):
            return ""
        
        return outFilePath
        
    
    def runMikadoPrepare(self,jsonconf, out_dir="",verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Wrapper to run mikado prepare
        """
        
        #check input files exist
        if not check_files_exist(jsonconf):
            print("Please check the input configuration to mikado.")
            return ""
        if not out_dir:
            out_dir=os.getcwd()

        newOpts={"--output-dir":out_dir,"--json-conf":jsonconf}
        
        #merge with kwargs
        mergedOpts={**kwargs,**newOpts}
        
        status=self.runMikado("prepare",verbose=verbose,quiet=quiet,logs=logs,objectid=objectid,**mergedOpts)
        
        if not status:
            print("Mikado prepare failed for:"+jsonconf)
            return ""
        
        #check if bam file exists
        if not checkPathsExists(out_dir):
            return ""
        
        return out_dir
        
        
        
    def runMikadoSerialise(self,jsonconf,blastTargets,orfs,xml,out_dir="",verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Wrapper to run mikado serialise
        """
        #check input files exist
        if not check_files_exist(blastTargets,orfs,xml):
            print("Please check the input to mikado.")
            return ""
        if not out_dir:
            out_dir=os.getcwd()
        
        newOpts={"--json-conf":jsonconf,"--blast_targets":blastTargets,"--xml":xml,"--orfs":orfs,"--output-dir":out_dir}
        
        #merge with kwargs
        mergedOpts={**kwargs,**newOpts}
        
        status=self.runMikado("serialise",verbose=verbose,quiet=quiet,logs=logs,objectid=objectid,**mergedOpts)
        
        if not status:
            print("Mikado serialise failed for:"+jsonconf)
            return ""
        
        #check if bam file exists
        if not checkPathsExists(out_dir):
            return ""
        
        return out_dir
        
        
    def runMikadoPick(self,jsonconf,out_dir="",verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Wrapper to run mikado pick
        """
        #check input files exist
        if not check_files_exist(jsonconf):
            print("Please check the input to mikado.")
            return ""
        if not out_dir:
            out_dir=os.getcwd()
        
        newOpts={"--json-conf":jsonconf}
        
        #merge with kwargs
        mergedOpts={**kwargs,**newOpts}
        
        status=self.runMikado("pick",verbose=verbose,quiet=quiet,logs=logs,objectid=objectid,**mergedOpts)
        
        if not status:
            print("Mikado pick failed for:"+jsonconf)
            return ""
        
        #check if bam file exists
        if not checkPathsExists(out_dir):
            return ""
        
        return out_dir
        
        
    def runMikado(self,sub_command,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Wrapper to run mikado
        """
        
        #override existing arguments
        mergedArgsDict={**self.passedArgumentDict,**kwargs}
       
        mikado_Cmd=['mikado',sub_command]
        #add options
        mikado_Cmd.extend(parse_unix_args(self.valid_args,mergedArgsDict))
                
        #print("Executing:"+" ".join(mergedArgsDict))
        
        #start ececution
        status=executeCommand(mikado_Cmd,verbose=verbose,quiet=quiet,logs=logs,objectid=objectid)
        if not status:
            print_boldred("mikado failed")
        #return status
        return status
        
        
        
        
        
        
class Ribocode(RNASeqTools):
    def __init__(self,**kwargs):
        self.programName="RiboCode"
        self.depList=[self.programName]
        #check if program exists
        if not check_dependencies(self.depList):
            raise Exception("ERROR: "+ self.programName+" not found.")
        
        self.valid_args=[]        
        self.passedArgumentDict=kwargs
        
        
    def runRibocode(self,gtf,genome,bam,l="no",outsuffix="ribocode_out",verbose=False,quiet=False,logs=True,objectid="NA"):
        """Wrapper to run ribocode in one step
        """
        
        #check input
        if not check_files_exist(gtf,genome,bam):
            print_boldred("Please check input files for Ribocode")
            return ""
        
        out_dir=pu.get_file_directory(gtf)
        outFile=os.path.join(out_dir,outsuffix)
        
        newOpts={"-g":gtf,"f":genome,"-r":bam,"-l":l,-o:outFile}
        
        ribocode_Cmd=['RiboCode_onestep']
        ribocode_Cmd.extend(parse_unix_args(self.valid_args,newOpts))
        
        status=executeCommand(ribocode_Cmd,verbose=verbose,quiet=quiet,logs=logs,objectid=objectid)
        if not status:
            print_boldred("ribocode failed")
            return ""
        
        return outFile
        
        
        

        
       
        
        
        
        
        
        
        
        
        
        
        