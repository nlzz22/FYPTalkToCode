import subprocess
from subprocess import STDOUT,PIPE
import os
import time

class CodeFormatter:
    def __init__(self, tempreadfilename="CFtemp.c", tempwritefilename="CFtemp2.c"):
        self.temp_read_file = tempreadfilename
        self.temp_write_file = tempwritefilename
        
    def format_code(self, code):
        self.copy_code_to_file(code)
        self.format_code_with_astyle()

        return self.get_formatted_code()

    def copy_code_to_file(self, code):
        with open(self.temp_read_file, "w") as fileobject:
            fileobject.write(code)

    ## This function runs AStyle C code formatting on the @param: tempreadfilename file.
    ## The resulting formatted code will be found at the @param: tempwritefilename file.
    def format_code_with_astyle(self):
        CREATE_NO_WINDOW = 0x08000000

        # run the AStyle C program
        cmd = ['./AStyle.exe ']

        read_fileobject = open(self.temp_read_file, "r")
        write_fileobject = open(self.temp_write_file, "w")

        proc = subprocess.Popen(cmd, stdin=read_fileobject, stdout=write_fileobject, stderr=STDOUT, creationflags=CREATE_NO_WINDOW)

        read_fileobject.close()
        write_fileobject.close()

        proc.communicate() # blocks until the subprocess completes.

    def get_formatted_code(self):
        with open(self.temp_write_file, "r") as fileobject:
            lines = fileobject.readlines()
        complete_code = ""

        for line in lines:
            if line.strip() != "":
                complete_code += line

        return complete_code

if __name__ == "__main__":
    # For testing.
    cf = CodeFormatter()
    print cf.format_code(" #include<stdio.h>\n\nint main(void){\nint max = 1;\nreturn 0;\n\t}")


        
        
