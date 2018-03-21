#!/usr/bin/env python2

import subprocess
from subprocess import STDOUT,PIPE
import os
from PlatformChecker import *

class CodeFormatter:
    def __init__(self):
        self.language = "C"
        self.config_file = os.path.join("uncrustify", "cfg", "defaults.cfg")
        self.exe_file = os.path.join("uncrustify", "uncrustify.exe")
        
    def format_code(self, code):
        self.code = code
        try:
            formatted_code = self.format_code_with_uncrustify(code)
            formatted_code = self.process_code(formatted_code)
        except:
            formatted_code = self.code

        return formatted_code

    def format_code_with_uncrustify(self, code):
        CREATE_NO_WINDOW = 0x08000000

        cmd = [self.exe_file, '-l', self.language, '-c', self.config_file]
        proc = ""

        if is_windows_os():
            # Windows specific command
            proc = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, creationflags=CREATE_NO_WINDOW)
        else:
            # Other os's command
            proc = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
            
        formatted_code, err = proc.communicate("{}\n".format(code))

        return formatted_code

    def process_code(self, code):
        result = []
        parts = code.split("\n")
        parts = parts[:-2] # Remove additional output from uncrustify which is not part of the program

        for part in parts:
            if part.strip() == "":
                continue
            result.append(part)
        return "\n".join(result)
            

if __name__ == "__main__":
    # For testing.
    cf = CodeFormatter()
    print cf.format_code(" #include<stdio.h>\n\nint main(void){\nint max = 1;\nreturn 0;\n\t}")


        
        
