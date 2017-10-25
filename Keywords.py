class Keywords:
    def __init__(self):
        list_keywords = ["equal", "end equal", "array index", "begin if", "greater than", "greater than equal"]
        list_keywords += ["less than", "less than equal", "not equal", "then", "else", "end if", "for", "loop"]
        list_keywords += ["condition", "begin", "plus", "minus", "declare", "integer", "float", "double", "long"]
        list_keywords += ["end for", "times", "divide", "modulo", "end declare", "array", "with", "size", "return"]
        list_keywords += ["void", "create function", "return type", "parameter", "end function", "while", "end while"]
        list_keywords += ["call function", "type", "string", "end string", "character"]
        self.keywords = list_keywords
    
    def get_keywords(self):
        return self.keywords



