class Keywords:
    def __init__(self):
        list_keywords = ["array", "begin", "call", "character", "condition", "create", "declare", "divide"]
        list_keywords += ["double", "else", "end", "equal", "float", "for", "function", "greater", "if", "index", "integer"]
        list_keywords += ["less", "long", "loop", "minus", "modulo", "not", "parameter", "plus", "return", "size", "string"]
        list_keywords += ["than", "then", "times", "type", "void", "while", "with", "undo", "default", "break", "switch", "case"]
        list_keywords += ["and", "or", "symbol"]
        self.keywords = list_keywords
    
    def get_keywords(self):
        return self.keywords
