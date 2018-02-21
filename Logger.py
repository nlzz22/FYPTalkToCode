#!/usr/bin/env python2

class Logger:
    def __init__(self, filename="log.txt"):
        self.filename = filename
        self.new_instance = True

        # wipe contents first.
        open(filename, 'w').close()

    def log(self, line):
        prepend_text = "\n"
        if self.new_instance:
            prepend_text = ""
            self.new_instance = False
        
        file_object = open(self.filename, "a")
        file_object.write(prepend_text + line)
        file_object.close()
