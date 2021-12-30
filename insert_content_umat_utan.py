#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 11:17:55 2021

@author: jfriedlein

@todo
- For vectorized umats and utans we need to change some things (umat_nbr is number followed by "v", ...)

@note
- The script was developed for Linux and has not yet been tested under Windows
  (neither Windows-Python nor Windows-LS-Dyna). This will be tested soon.
- The relevant differences in the object files for this script are the "#include ..."
  in the Windows-LS-Dyna "dyn21*.f" files. However, inserting the normal "include ..." before them appears okay.
"""

import os
import shutil
import subprocess
from datetime import datetime

## Define some colours for nicer output (e.g. error in red)
# From [https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal]
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


## USER-INPUT #################################################################    
# Name of original dyn21 files will be appended by the following phrase
phrase_original = '_ORIGINAL'

# name and path of source code file
name_content_umat_utan = 'content_umat_utan.f'
path_to_content_umat_utan='.'+'/'+name_content_umat_utan
path_to_tmp_content = '.'+'/'+'tmp_content.f'

# phrases used in the source code file and entered into the dyn21 files
phrase_CUSTOM_SECTION_UMAT_INCLUDE_START = '!CUSTOM_SECTION_UMAT_INCLUDE_START'
phrase_CUSTOM_SECTION_UMAT_INCLUDE_END = '!CUSTOM_SECTION_UMAT_INCLUDE_END'
phrase_CUSTOM_SECTION_UTAN_INCLUDE_START = '!CUSTOM_SECTION_UTAN_INCLUDE_START'
phrase_CUSTOM_SECTION_UTAN_INCLUDE_END = '!CUSTOM_SECTION_UTAN_INCLUDE_END'

phrase_CUSTOM_SECTION_UMAT_START = 'c\n!CUSTOM_SECTION_UMAT_START\n'
phrase_CUSTOM_SECTION_UMAT_END = '!CUSTOM_SECTION_UMAT_END\nc\n'
phrase_CUSTOM_SECTION_UTAN_START = 'c\n!CUSTOM_SECTION_UTAN_START\n'
phrase_CUSTOM_SECTION_UTAN_END = '!CUSTOM_SECTION_UTAN_END\nc\n'

# @note End the strings with a line break "\n" to make sure that for instance
# the phrase "end" is not triggered by a line containing "endif"
final_lines_subroutine=[]
final_lines_subroutine.append('      return\n')
final_lines_subroutine.append('      end\n')

# Catch phrases for umat and utan subroutine
phrase_subroutine_umat = '      subroutine umat'
phrase_subroutine_utan = '      subroutine utan'


## class to collect the LS-Dyna releases and the related names and paths
# @note We added the extensions as "ext_*" variables separately in case we use ".F" or ".f"
class LSD_release:
    def __init__(self, path_to_dyn21, name_dyn21umats, ext_dyn21umats, name_dyn21utan, ext_dyn21utan):
        self.path_to_dyn21 = path_to_dyn21
        self.name_dyn21umats = name_dyn21umats
        self.ext_dyn21umats = ext_dyn21umats
        self.name_dyn21utan = name_dyn21utan
        self.ext_dyn21utan = ext_dyn21utan
        self.path_to_tmp_input_for_utan = path_to_dyn21 + '/' + 'tmp_dyn21.f'


LSD_R920_LT7 = LSD_release(
    '../ls-dyna_smp_d_r920_x64_redhat59_ifort160_MASK', 
    'dyn21', '.f',
    'dyn21', '.f'
    )
LSD_R920 = LSD_release(
    '../ls-dyna_smp_d_r920_x64_redhat59_ifort131_usermat_MASK', 
    'dyn21', '.f',
    'dyn21', '.f'
    )

LSD_R102_mpp= LSD_release(
    '../ls-dyna_mpp_d_R10_2_0_x64_centos65_ifort160_sse2_intelmpi-2018_MASK', 
    'dyn21', '.f',
    'dyn21', '.f'
    )

LSD_R111_LT7 = LSD_release(
    '../ls-dyna_smp_d_R11_1_0_x64_redhat65_ifort160_sse2_MASK', 
    'dyn21umats', '.f',
    'dyn21utan', '.f'
    )
LSD_R111 = LSD_release(
    '../ls-dyna_smp_d_R11_1_0_x64_redhat65_ifort160_sse2_usermat_MASK', 
    'dyn21umats', '.f',
    'dyn21utan', '.f'
    )

LSD_R130 = LSD_release(
    '../ls-dyna_smp_d_R13_0_0_x64_centos610_ifort190_MASK',
    'dyn21umats', '.f',
    'dyn21utan', '.f'
    )
    
## USER-INPUT #################################################################
# Choose the LS-Dyna releases defined above that shall be modified
LSD_versions_to_be_inserted = [ LSD_R920_LT7 , LSD_R111_LT7 , LSD_R130 ]
# Shall the modified Fortran files directly be compiled (requires the correct compiler, etc.)
compile_Fortran_files = False


## EXECUTION ##################################################################      
# clear terminal [https://stackoverflow.com/questions/2084508/clear-terminal-in-python]
os.system('cls' if os.name == 'nt' else 'clear')

# Check for existence of "content_umat_utan" file, which is essential for the script
if os.path.isfile(path_to_content_umat_utan) != True:
    print(bcolors.FAIL + "ERROR<< File '"+name_content_umat_utan+"' does not exist. Create this file or name it correctly." + bcolors.ENDC)
    exit()

# Loop over all the LSD-versions in the list "LSD_versions_to_be_inserted"
for LSD_version in LSD_versions_to_be_inserted:
    # Retrieve name and paths
    path_to_dyn21 = LSD_version.path_to_dyn21
    name_dyn21umats =  LSD_version.name_dyn21umats
    ext_dyn21umats =  LSD_version.ext_dyn21umats
    name_dyn21utan =  LSD_version.name_dyn21utan
    ext_dyn21utan =  LSD_version.ext_dyn21utan
    path_to_tmp_input_for_utan =  LSD_version.path_to_tmp_input_for_utan

    # print some information to indicate which version we work on
    print(bcolors.OKBLUE + "We operate on LS-Dyna release "+path_to_dyn21 + bcolors.ENDC)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)
    
    path_to_used_content = path_to_content_umat_utan    
    
    # for dyn21utan
    # Collect the utan numbers to be replaced
    list_of_content_utan_nbrs = []
    with open(path_to_content_umat_utan, 'r') as content_umat_utan: # read only 
        for line_content in content_umat_utan:
            if ( phrase_subroutine_utan in line_content ):
                utan_nbr = int(line_content[len(phrase_subroutine_utan):len(phrase_subroutine_utan)+2])
                list_of_content_utan_nbrs.append(utan_nbr)  
    
    print("The following utans will be replaced: ", list_of_content_utan_nbrs," ...")
    
    path_to_dyn21utan = path_to_dyn21+'/'+name_dyn21utan+ext_dyn21umats
    
    path_to_dyn21utan_original = path_to_dyn21+'/'+name_dyn21utan+phrase_original+ext_dyn21utan
    
    if os.path.isfile(path_to_dyn21utan_original) != True:
        shutil.copy2(path_to_dyn21utan,  path_to_dyn21utan_original)
    
    line_counter = 1
    write_line = False
    overwriting_subroutine = False
    with open(path_to_dyn21utan, 'w') as dyn21utan: # create new file or overwrite old
        with open(path_to_dyn21utan_original, 'r') as dyn21utan_original: # read only
                for index, line_original in enumerate(dyn21utan_original):
                    # Insert the custom includes from the "content_umat_utan"
                    if ( line_counter==1 ):
                        write_line = False
                        with open(path_to_used_content, 'r') as content_umat_utan: # read only 
                            for line_content in content_umat_utan:
                                if (phrase_CUSTOM_SECTION_UTAN_INCLUDE_START in line_content):
                                    write_line = True
                                if (phrase_CUSTOM_SECTION_UTAN_INCLUDE_END in line_content):
                                    # write the final line
                                    dyn21utan.write( line_content )
                                    # but after that end the writing
                                    write_line = False
                                if ( write_line ):
                                    dyn21utan.write( line_content )
                    # Overwrite the utan routines with the content from "content_umat_utan"
                    # Look for the subroutine_utan phrase
                    if ( phrase_subroutine_utan in line_original ):
                        # Extract what follows after the catch phrase
                        phrase_followUp = line_original[len(phrase_subroutine_utan):len(phrase_subroutine_utan)+2]
                        phrase_followUpUp = line_original[len(phrase_subroutine_umat)+2]
                        # if a numerical value follows and after the value an opening bracket,
                        # then we found a normal utan41 to utan50 routine and continue
                        # We need to check the following character for two options, because sometimes it is "utan43(" and sometimes "utan43 ("
                        if phrase_followUp.isnumeric() and (phrase_followUpUp=='(' or phrase_followUpUp==' '):
                            utan_nbr = int(phrase_followUp)
                            # Check whether the found subroutine needs to be replaced by the content from "content_umat_utan"
                            utan_index = [x for x in list_of_content_utan_nbrs if utan_nbr==x]
                            # Check whether the list is empty, if not continue
                            if ( utan_index ):
                                # Now that we found the routine to be overwritten, we can log that state
                                overwriting_subroutine = True
                                # To indicate which parts of the file have been overwritten we add markers
                                dyn21utan.write(phrase_CUSTOM_SECTION_UTAN_START)
                                # To make sure the interfaces are good, we use the interface
                                # from the original file and replace ones from the "content_umat_utan" file
                                current_line = line_original
                                next_line = dyn21utan_original.readlines(1)
                                dyn21utan.write( current_line )
                                dyn21utan.write( next_line[0] )
                                write_line = False
                                pending_end = 0
                                with open(path_to_used_content, 'r') as content_umat_utan: # read only 
                                    pending_start = 0
                                    for line_content in content_umat_utan:
                                        if ( pending_start == 2 ):    
                                            pending_start = 0
                                            write_line = True
                                        if ( pending_start == 1 ):
                                            pending_start+=1
                                        if ( phrase_subroutine_utan in line_content ):
                                            utan_nbr_internal = int(line_content[len(phrase_subroutine_utan):len(phrase_subroutine_utan)+2])
                                            if ( utan_nbr_internal==utan_nbr ):
                                                pending_start = 1
                                        if ( write_line ):
                                            dyn21utan.write( line_content )
                                            if ( final_lines_subroutine[0] in line_content  ):
                                                pending_end = 1
                                            if ( (pending_end == 1) and (final_lines_subroutine[1] in line_content) ):
                                                dyn21utan.write(phrase_CUSTOM_SECTION_UTAN_END)
                                                break
                    # Only add the original lines if we do not intend to overwrite them                    
                    if (overwriting_subroutine==False):
                        dyn21utan.write( line_original )   
                    # Find the end of the subroutine that we currently overwrite
                    elif ( final_lines_subroutine[1] in line_original ):
                        overwriting_subroutine = False
    
                    line_counter = line_counter + 1
                    
    print("... utans replaced.")
    
    ## Check the existence of the "phrase_original" files
    # for dyn21umats
    path_to_dyn21umats = path_to_dyn21+'/'+name_dyn21umats+ext_dyn21umats
    
    # For newer releases separate umat and utan files exist
    if (name_dyn21umats!=name_dyn21utan):
        path_to_dyn21umats_original = path_to_dyn21+'/'+name_dyn21umats+phrase_original+ext_dyn21umats
    
        if os.path.isfile(path_to_dyn21umats_original) != True:
            shutil.copy2(path_to_dyn21umats,  path_to_dyn21umats_original)
    # For older releases umats and utan are in the same file, so we do not copy the same file twice
    # To ensure that we modify the umat and utan in the same file, we use the updated umat file to enter the new utans
    else:
        shutil.copy2(path_to_dyn21utan,  path_to_tmp_input_for_utan)
        path_to_dyn21umats_original = path_to_tmp_input_for_utan
    
    # Collect the umat numbers to be replaced
    list_of_content_umat_nbrs = []
    with open(path_to_content_umat_utan, 'r') as content_umat_utan: # read only 
        for line_content in content_umat_utan:
            if ( phrase_subroutine_umat in line_content ):
                umat_nbr = int(line_content[len(phrase_subroutine_umat):len(phrase_subroutine_umat)+2])
                list_of_content_umat_nbrs.append(umat_nbr)
    
    print("The following umats will be replaced: ", list_of_content_umat_nbrs, " ...")
    
    ## Read the "phrase_original" files, insert the content from "name_content_umat_utan" and save the merged file as the normal dyn21* files
    # for umats
    # @note: For R920, we need to write the umat update into the previously modified file
    line_counter = 1
    write_line = False
    overwriting_subroutine = False
    with open(path_to_dyn21umats, 'w') as dyn21umats: # create new file or overwrite old
        with open(path_to_dyn21umats_original, 'r') as dyn21umats_original: # read only
            
                for line_original in dyn21umats_original:
                    # Insert the custom includes from the "content_umat_utan"
                    if ( line_counter==1 ):
                        write_line = False
                        with open(path_to_used_content, 'r') as content_umat_utan: # read only 
                            for line_content in content_umat_utan:
                                if (phrase_CUSTOM_SECTION_UMAT_INCLUDE_START in line_content):
                                    write_line = True
                                if (phrase_CUSTOM_SECTION_UMAT_INCLUDE_END in line_content):
                                    # write the final line
                                    dyn21umats.write( line_content )
                                    # but after that end the writing
                                    write_line = False
                                if ( write_line ):
                                    dyn21umats.write( line_content )
                    # Overwrite the umat routines with the content from "content_umat_utan"
                    # Look for the subroutine_umat phrase
                    if ( phrase_subroutine_umat in line_original ):
                        # Extract what follows after the catch phrase
                        phrase_followUp = line_original[len(phrase_subroutine_umat):len(phrase_subroutine_umat)+2]
                        phrase_followUpUp = line_original[len(phrase_subroutine_umat)+2]
                        # if a numerical value follows and after the value an opening bracket,
                        # then we found a normal umat41 to umat50 routine and continue
                        # The second criterion checking the character after the number ensures that we don't find umat41v to umat50v
                        # We need to check the following character for two options, because sometimes it is "umat43(" and sometimes "umat43 ("
                        if phrase_followUp.isnumeric() and (phrase_followUpUp=='(' or phrase_followUpUp==' '):
                            umat_nbr = int(phrase_followUp)
                            # Check whether the found subroutine needs to be replaced by the content from "content_umat_utan"
                            umat_index = [x for x in list_of_content_umat_nbrs if umat_nbr==x]
                            # Check whether the list is empty, if not continue
                            if ( umat_index ):
                                # Now that we found the routine to be overwritten, we can log that state
                                overwriting_subroutine = True
                                # To indicate which parts of the file have been overwritten we add markers
                                dyn21umats.write(phrase_CUSTOM_SECTION_UMAT_START)
                                write_line = False
                                pending_end = 0
                                with open(path_to_used_content, 'r') as content_umat_utan: # read only 
                                    for line_content in content_umat_utan:
                                        if ( phrase_subroutine_umat in line_content ):
                                            umat_nbr_internal = int(line_content[len(phrase_subroutine_umat):len(phrase_subroutine_umat)+2])
                                            if ( umat_nbr_internal==umat_nbr ):
                                                write_line = True                                  
                                        if ( write_line ):
                                            dyn21umats.write( line_content )
                                            if ( final_lines_subroutine[0] in line_content  ):
                                                pending_end = 1
                                            if ( (pending_end == 1) and (final_lines_subroutine[1] in line_content) ):
                                                dyn21umats.write(phrase_CUSTOM_SECTION_UMAT_END)
                                                break
                    # Only add the original lines if we do not intend to overwrite them                    
                    if (overwriting_subroutine==False):
                        dyn21umats.write( line_original )   
                    # Find the end of the subroutine that we currently overwrite
                    elif ( final_lines_subroutine[1] in line_original ):
                        overwriting_subroutine = False
    
                    line_counter = line_counter + 1
    
    print("... umats replaced.")

    if ( compile_Fortran_files ):
        ## Compile the just modified Fortran files into the ls-dyna executable
        print(bcolors.OKBLUE + "\nExecute the command 'make' in the '"+path_to_dyn21+"' directory ...\n" + bcolors.ENDC)    

        # Execute the command "make" in the "path_to_dyn21" directory
        process = subprocess.Popen(['make',path_to_dyn21], cwd=path_to_dyn21, shell=True)
        
        # Wait for the subprocess to finish
        exit_code = process.wait()
        if exit_code != 0:
            print(bcolors.FAIL + "\n... 'make' failed.\n" + bcolors.ENDC)
        else:   
            print(bcolors.OKGREEN + "\n... Finished 'make'.\n" + bcolors.ENDC)                

print(bcolors.OKBLUE + "\nFinished execution." + bcolors.ENDC)    

# note: return as soon as all have finished "exit_codes = [p.wait() for p in p1, p2]" [https://coderedirect.com/questions/157584/wait-process-until-all-subprocess-finish]


## Outsourced, Todos:    

# The following is useless, because the files we call internally also use the old paths
## @todo Some people might use (include "../"), catch this, maybe also protect against different formatting (include  "../")
## @todo It is possible that we mess up some LS-Dyna include paths, however they usually don't refer to external files "../"
#replace_relatives_paths = True
#relative_path_between_target_file_and_development_file = '../'
#trigger_phrase_for_include_path_change = "      include '../"

## Replace relative paths inside the "content_umat_utan" file to enable the compiler to find the files
#if replace_relatives_paths:
#    #update_relative_paths(path_to_content_umat_utan,trigger_phrase_for_include_path_change,relative_path_between_target_file_and_development_file)
#    with open(path_to_tmp_content, 'w') as temp_content: # open for updating (reading and writing)
#        with open(path_to_content_umat_utan, 'r') as content_umat_utan: # open for updating (reading and writing)
#            for line_content in content_umat_utan:
#                if ( trigger_phrase_for_include_path_change in line_content ):
#                    pos_of_path_start = line_content.find("'")
#                    new_line= line_content[:pos_of_path_start+1]+relative_path_between_target_file_and_development_file+line_content[pos_of_path_start+1:]
#                else:
#                    new_line = line_content
#                temp_content.write(new_line)    
#    path_to_used_content = path_to_tmp_content
#else:
#    path_to_used_content = path_to_content_umat_utan       
