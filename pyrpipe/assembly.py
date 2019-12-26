#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 15:21:01 2019

@author: usingh
"""

from pyrpipe.pyrpipe_utils import *
from pyrpipe.pyrpipe_engine import *

class Assembly:
    """This class represents an abstract parent class for all programs which can perfrom transcripts assembly.
    """
    def __init__(self):
        self.category="Assembler"
    def perform_assembly(bam_file):
        """Function to perform assembly using a bam file as input. Inherited by all children.
        
        Parameters
        ----------
        bam_file (string): Path to the bam file.
        
        
        Returns
        --------
        string: path to output GTF or output directory depending on the specific assembly program.
        """
        pass

class Stringtie(Assembly):
    """This class represents Stringtie program for transcript assembly.
        
        Parameters
        ----------
        reference_gtf: string
            Path to the reference gtf file. If a valid gtf file is provided the option -G will be set to the gtf file. This can't
            be overriden later when calling functions of this class.
        arg2: dict
            Options passed to stringtie. Some of these could be overridden later when calling functions of this class.
            Format to pass the arguments:
        """
    def __init__(self,reference_gtf="",**kwargs):
        
        super().__init__()
        self.program_name="stringtie"
        #check if stringtie exists
        if not checkDep([self.program_name]):
            raise Exception("ERROR: "+ self.program_name+" not found.")
        self.valid_args_list=['-G','--version','--conservative','--rf','--fr','-o','-l',
                            '-f','-L','-m','-a','-j','-t','-c','-s','-v','-g','-M',
                            '-p','-A','-B','-b','-e','-x','-u','-h','--merge','-F','-T','-i']
        
        #keep the passed arguments
        self.passed_args_dict=kwargs
        
        #check the reference GTF
        if len(reference_gtf)>0 and check_files_exist(reference_gtf):
            self.reference_gtf=reference_gtf
            self.passed_args_dict['-G']=reference_gtf
        
    def perform_assembly(self,bam_file,out_suffix="_stringtie",overwrite=True,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Function to run stringtie using a bam file. Manages the outout file names and returns it.
                
        Parameters
        ----------
        bam_file (string): path to the bam file
        out_suffix (string): Suffix for the output gtf file
        overwrite (bool): Overwrite if output file already exists.
        verbose (bool): Print stdout and std error
        quiet (bool): Print nothing
        logs (bool): Log this command to pyrpipe logs
        objectid (str): Provide an id to attach with this command e.g. the SRR accession. This is useful for debugging, benchmarking and reports.
        kwargs (dict): Options to pass to stringtie. This will override the existing options 
                       in self.passed_args_dict (only replace existing arguments and not replace all the arguments).
            
        Returns
        -------
        string: path to output GTF file
        """
        
        #create path to output file
        fname=get_file_basename(bam_file)
        out_dir=get_file_directory(bam_file)
        out_gtf_file=os.path.join(out_dir,fname+out_suffix+".gtf")
        
        """
        Handle overwrite
        """
        if not overwrite:
            #check if file exists. return if yes
            if os.path.isfile(out_gtf_file):
                print("The file "+out_gtf_file+" already exists. Exiting..")
                return out_gtf_file
        
        #Add output file name and input bam
        new_opts={"-o":out_gtf_file,"--":(bam_file,)}
        merged_opts={**kwargs,**new_opts}
        
        #call stringtie
        status=self.run_stringtie(verbose=verbose,quiet=quiet,logs=logs,objectid=objectid,**merged_opts)
        
        if status:
            #check if sam file is present in the location directory of sraOb
            if check_files_exist(out_gtf_file):
                return out_gtf_file
        else:
            return ""
        
    def performStringtieMerge(self,*args,out_suffix="_stringtieMerge",overwrite=True,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Function to run stringtie merge.
        Parameters
        ----------
        args (tuple): path to gtf files to merge
        out_suffix (string): Suffix for output gtf file name
        arg2: tuple
            input Gtf files
        overwrite (bool): Overwrite if output file already exists.
        verbose (bool): Print stdout and std error
        quiet (bool): Print nothing
        logs (bool): Log this command to pyrpipe logs
        objectid (str): Provide an id to attach with this command e.g. the SRR accession. This is useful for debugging, benchmarking and reports.
        kwargs (dict): Options to pass to stringtie. This will override the existing options 
                       in self.passed_args_dict (only replace existing arguments and not replace all the arguments).
            
        Returns
        -------
        string: path to the merged GTF file
        """
        
        if len(args) < 1:
            print("ERROR: No input gtf for stringtie merge.")
            return ""
        
        #create path to output sam file
        fname=get_file_basename(args[0])
        out_dir=get_file_directory(args[0])
        out_gtf_file=os.path.join(out_dir,fname+out_suffix+".gtf")
        
        if not overwrite:
            #check if file exists. return if yes
            if os.path.isfile(out_gtf_file):
                print("The file "+out_gtf_file+" already exists. Exiting..")
                return out_gtf_file
        
        #Add merge flag, output file name and input bam
        new_opts={"--merge":"","-o":out_gtf_file,"--":args}
        
        merged_opts={**kwargs,**new_opts}
        
        #call stringtie
        status=self.run_stringtie(verbose=verbose,quiet=quiet,logs=logs,objectid=objectid,**merged_opts)
        
        if status:
            #check if sam file is present in the location directory of sraOb
            if check_files_exist(out_gtf_file):
                return out_gtf_file
        else:
            return ""
        
        
        
            
    
    def run_stringtie(self,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Wrapper for running stringtie. This can be used to run stringtie without using perform_assembly() function.
        
        Parameters
        ----------
        verbose (bool): Print stdout and std error
        quiet (bool): Print nothing
        logs (bool): Log this command to pyrpipe logs
        objectid (str): Provide an id to attach with this command e.g. the SRR accession. This is useful for debugging, benchmarking and reports.
        kwargs (dict): Options to pass to stringtie. This will override the existing options 
                       in self.passed_args_dict (only replace existing arguments and not replace all the arguments).
            
        Returns
        -------
        bool: status of stringtie command.
        """
            
        #override existing arguments
        merged_args_dict={**self.passed_args_dict,**kwargs}
       
        stie_cmd=['stringtie']
        #add options
        stie_cmd.extend(parse_unix_style_args(self.valid_args_list,merged_args_dict))        
        
                
        #start ececution
        status=execute_command(stie_cmd,verbose=verbose,quiet=quiet,logs=logs,objectid=objectid)
        if not status:
            print_boldred("stringtie failed")
        
        #return status
        return status
    
    
    
class Cufflinks(Assembly):
    def __init__(self,reference_gtf="",**kwargs):
        """Stringtie constructor. Initialize stringtie parameters.
        
        Parameters
        ----------
        arg1: string
            Path to the reference gtf file.
        arg2: dict
            Options passed to stringtie. These could be overridden later when executing cufflinks.
        """
        super().__init__()
        self.program_name="cufflinks"
        #check if stringtie exists
        if not checkDep([self.program_name]):
            raise Exception("ERROR: "+ self.program_name+" not found.")
            
        
        
        self.cufflinksArgsList=['-h','--help','-o','--output-dir','-p','--num-threads','--seed','-G','--GTF','-g','--GTF-guide','-M','--mask-file','-b','--frag-bias-correct','-u','--multi-read-correct','--library-type','--library-norm-method',
'-m','--frag-len-mean','-s','--frag-len-std-dev','--max-mle-iterations','--compatible-hits-norm','--total-hits-norm','--num-frag-count-draws','--num-frag-assign-draws','--max-frag-multihits','--no-effective-length-correction',
'--no-length-correction','-N','--upper-quartile-norm','--raw-mapped-norm','-L','--label','-F','--min-isoform-fraction','-j','--pre-mrna-fraction','-I','--max-intron-length','-a','--junc-alpha','-A','--small-anchor-fraction',
'--min-frags-per-transfrag','--overhang-tolerance','--max-bundle-length','--max-bundle-frags','--min-intron-length','--trim-3-avgcov-thresh','--trim-3-dropoff-frac','--max-multiread-fraction','--overlap-radius',
'--no-faux-reads','--3-overhang-tolerance','--intron-overhang-tolerance','-v','--verbose','-q','--quiet','--no-update-check']

        self.cuffcompareArgsList=['-h','-i','-r','-R','-Q','-M','-N','-s','-e','-d','-p','-C','-F','-G','-T','-V']
        self.cuffquantArgsList=['-o','--output-dir','-p','--num-threads','-M','--mask-file','-b','--frag-bias-correct','-u','--multi-read-correct','--library-type','-m','--frag-len-mean','-s','--frag-len-std-dev','-c','--min-alignment-count',
'--max-mle-iterations','-v','--verbose','-q','--quiet','--seed','--no-update-check','--max-bundle-frags','--max-frag-multihits','--no-effective-length-correction','--no-length-correction','--read-skip-fraction',
'--no-read-pairs','--trim-read-length','--no-scv-correction']
        self.cuffdiffArgsList=['-o','--output-dir','-L','--labels','--FDR','-M','--mask-file','-C','--contrast-file','-b','--frag-bias-correct','-u','--multi-read-correct','-p','--num-threads','--no-diff','--no-js-tests','-T','--time-series',
'--library-type','--dispersion-method','--library-norm-method','-m','--frag-len-mean','-s','--frag-len-std-dev','-c','--min-alignment-count','--max-mle-iterations','--compatible-hits-norm','--total-hits-norm',
' -v','--verbose','-q','--quiet','--seed','--no-update-check','--emit-count-tables','--max-bundle-frags','--num-frag-count-draws','--num-frag-assign-draws','--max-frag-multihits','--min-outlier-p','--min-reps-for-js-test',
'--no-effective-length-correction','--no-length-correction','-N','--upper-quartile-norm','--geometric-norm','--raw-mapped-norm','--poisson-dispersion','--read-skip-fraction','--no-read-pairs','--trim-read-length','--no-scv-correction']
        self.cuffnormArgsList=['-o','--output-dir','-L','--labels','--norm-standards-file','-p','--num-threads','--library-type','--library-norm-method','--output-format','--compatible-hits-norm','--total-hits-norm','-v','--verbose','-q','--quiet','--seed','--no-update-check']
        self.cuffmergeArgsList=['h','--help','-o','-g','–-ref-gtf','-p','–-num-threads','-s','-–ref-sequence']
        
        self.valid_args_list=getListUnion(self.cufflinksArgsList,self.cuffcompareArgsList,self.cuffquantArgsList,self.cuffdiffArgsList,self.cuffnormArgsList,self.cuffmergeArgsList)
        
        #keep the passed arguments
        self.passed_args_dict=kwargs
        
        #check the reference GTF
        if len(reference_gtf)>0 and check_files_exist(reference_gtf):
            self.reference_gtf=reference_gtf
            self.passed_args_dict['-g']=reference_gtf
    
    
    def perform_assembly(self,bam_file,out_suffix="_cufflinks",overwrite=True,**kwargs):
        """Function to run cufflinks with BAM file as input.
                
        Parameters
        ----------
        arg1: string
            path to bam file
        arg2: string
            Suffix for the output gtf file
        arg3: bool
            Overwrite if output file already exists.
        arg4: dict
            Options to pass to stringtie. This will override the existing options self.passed_args_dict (only replace existing arguments and not replace all the arguments).
            
        Returns
        -------
        string
            path to output GTF file
        
        """
        
        #create path to output file
        fname=get_file_basename(bam_file)
        out_dir=get_file_directory(bam_file)
        out_gtf_file=os.path.join(out_dir,fname+out_suffix+".gtf")
        
        """
        Handle overwrite
        """
        if not overwrite:
            #check if file exists. return if yes
            if os.path.isfile(out_gtf_file):
                print("The file "+out_gtf_file+" already exists. Exiting..")
                return out_gtf_file
            
        #Add output file name and input bam
        new_opts={"-o":out_dir,"--":(bam_file,)}
        merged_opts={**kwargs,**new_opts}
        
        #call cufflinks
        status=self.runCufflinks(**merged_opts)
        
        if status:
            #move out_dir/transcripts.gtf to outfile
            moveFile(os.path.join(out_dir,"transcripts.gtf"),out_gtf_file)
            #check if sam file is present in the location directory of sraOb
            if check_files_exist(out_gtf_file):
                return out_gtf_file
        else:
            return ""
    
    def runCuffCommand(self,command,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Wrapper for running cuff* commands
        
        Parameters
        ----------
        command: string
            the command name
        arg2: dict
            Options passed to cuff command
        
        Returns
        -------
        bool
            return status of the command.
        """
        validCommands=['cuffcompare','cuffdiff', 'cufflinks', 'cuffmerge', 'cuffnorm', 'cuffquant']
        if command in validCommands:
            #override existing arguments
            merged_args_dict={**self.passed_args_dict,**kwargs}
       
            cuff_cmd=[command]
            #add options
            cuff_cmd.extend(parse_unix_style_args(self.valid_args_list,merged_args_dict))        
                  
            #start ececution
            status=execute_command(cuff_cmd,verbose=verbose,quiet=quiet,logs=logs,objectid=objectid)
            if not status:
                print_boldred("cufflinks failed")
                #return status
            return status
        else:
            print_boldred("Unknown command {}"+command)
            return False
    
    
    def runCufflinks(self,verbose=False,quiet=False,logs=True,objectid="NA",**kwargs):
        """Wrapper for running cufflinks
        
        Parameters
        ----------
        arg1: dict
            Options passed to cufflinks
        
        Returns
        -------
        bool
            status of cufflinks command.
        """
            
        #override existing arguments
        merged_args_dict={**self.passed_args_dict,**kwargs}
       
        cufflinks_cmd=['cufflinks']
        #add options
        cufflinks_cmd.extend(parse_unix_style_args(self.valid_args_list,merged_args_dict))        
        
        
        #start ececution
        status=execute_command(cufflinks_cmd,verbose=verbose,quiet=quiet,logs=logs,objectid=objectid)
        if not status:
            print_boldred("cufflinks failed")
        #return status
        return status