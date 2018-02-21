#!/usr/bin/env python2

class TextFileReader:
    def __init__(self, filename):
        self.filename = filename
        self.lines = self.read_all_lines()
        self.current_index = 0
        self.length = len(self.lines)

    def read_all_lines(self):
        with open(self.filename, "r") as readfile:
            return readfile.readlines()

    def get_length(self):
        return self.length

    def read_line(self):
        if self.current_index < self.get_length():
            line_to_read = self.lines[self.current_index]
            self.current_index += 1

            return line_to_read
        else:
            return ""
