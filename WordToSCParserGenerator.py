#!/usr/bin/env python2

with open("NewWordParser.py", "r") as readfile:
    get_next = False
    data = readfile.readlines()
    for line in data:
        line = line.strip()
        if get_next:
            print line
        elif "struct = " in line and "result_struct" not in line \
           and "return_struct" not in line:
            print line
        else:
            continue
        if line[-1:] == "\\":
            get_next = True
        else:
            get_next = False
            print "print parse_structural_command_to_code(struct)"
