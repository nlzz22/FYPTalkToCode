import subprocess
from subprocess import STDOUT,PIPE
import os

class CodeFormatter:
    def __init__(self):
        self.language = "C"
        self.config_file = "uncrustify/cfg/defaults.cfg"
        self.exe_file = "uncrustify/uncrustify.exe"
        
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
        proc = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, creationflags=CREATE_NO_WINDOW)
        formatted_code, err = proc.communicate(code + "\n")

        return formatted_code

    def process_code(self, code):
        result = ""
        parts = code.split("\n")
        parts = parts[:-2] # Remove additional output from uncrustify which is not part of the program

        for part in parts:
            if part.strip() == "":
                continue
            result += part + "\n"
        return result
            

if __name__ == "__main__":
    # For testing.
    cf = CodeFormatter()
    print cf.format_code(" #include<stdio.h>\n\nint main(void){\nint max = 1;\nreturn 0;\n\t}")


        
        
