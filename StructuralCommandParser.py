#!/usr/bin/env python2

import os.path,subprocess
from subprocess import STDOUT,PIPE
from PlatformChecker import *

SPECIAL_REJECT_SEQ = "Special Reject Sequence @#$%^&*()!"

def parse_structural_command_to_code(structural_command):
    defaultProgramHeader = "#c_program SampleProgram\n"
    defaultProgramHeader += "#include #access stdio h #access_end;;"

    defaultProgramEnd = " #program_end"

    # Get Hello World Program for testing
    #defaultProgramHeader += get_sample_hello_world_program_in_structured_command()
    
    defaultProgramHeader += structural_command
    defaultProgramHeader += defaultProgramEnd

    #print "Compiling Java Program from Martin\n"
    #java_compile_dir = os.path.join('TalkToCode', 'talk-to-code', 'src', 'ast', '*.java')
    #compile_java(java_compile_dir)
    #print "Finished compiling. Running the Java Program... \n"

    java_dir = os.path.join('TalkToCode', 'talk-to-code', 'src') # using os.path.join makes it platform independent.
    output = execute_java(java_dir, 'ast/ASTParser', defaultProgramHeader)

    return output


def compile_java(java_file):
    subprocess.check_call(['javac', java_file])

def execute_java(java_dir, java_file, stdin):
    CREATE_NO_WINDOW = 0x08000000
    
    current_dir = os.getcwd()

    # switch directory
    os.chdir(java_dir)

    # run the java program
    cmd = ['java ', java_file]
    proc = ""

    if is_windows_os():
        # Windows specific command
        proc = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, creationflags=CREATE_NO_WINDOW)
    else:
        # Other os's command
        proc = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        
    
    # pass input to java program
    stdout,stderr = proc.communicate(stdin)

    # switch back to original directory
    os.chdir(current_dir)

    return stdout

def get_sample_hello_world_program_in_structured_command():
    program_code = "#function_declare main int \n"
    program_code += "#function_start \n"
    program_code += "#function printf(#parameter #value \"Hello World!\\n\");; \n"
    program_code += "return #value 0;; \n"
    program_code += "#function_end;; \n"
    program_code += "#program_end\n"

    return program_code

if __name__ == "__main__":
    while True:
        struct = raw_input("please enter your structured command: ")
        print "Converted to : "
        print parse_structural_command_to_code(struct)
