import sys

class Token():
    reserved = {
        "scene",
        "location",
        "note",
        "clip",
        "enters",
        "left",
        "right",
        "up",
        "if",
        "then",
        "else",
        "set",
        "to",
        "semi"
        }
    directions = {"left","right","up"}
    stage_positions = {"left","right","far_left","far_right","middle"}
    top_stmt = {"scene","clip","option"}
    bottom_stmt = {"if","set"}
    misc_stmt = {"location","music","sound","load","jump"}
    reserved = reserved.union(directions)
    reserved = reserved.union(stage_positions)
    reserved = reserved.union(top_stmt)
    reserved = reserved.union(bottom_stmt)
    reserved = reserved.union(misc_stmt)
    def __init__(self):
        self.type = ""
        self.val = 0
        self.literal = ""
        self.line = 0
    def __str__(self):
        return self.type + " => " + self.literal

class Scanner():
    def __init__(self):
        self.start = 0
        self.current = 0
        self.line = 1
        self.source = ""
        self.tokens = []
    def tokenize(self, source):
        self.source = source
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.start = self.current
        self.add_token("eof")
        return self.tokens
    def scan_token(self):
        c = self.advance()
        if c == ":":
            self.add_token("colon")
        elif c == ";":
            self.add_token("semi")
        elif c == "[":
            self.add_token("l_bracket")
        elif c == "]":
            self.add_token("r_bracket")
        elif c == "(":
            self.add_token("l_paren")
        elif c == ")":
            self.add_token("r_paren")
        elif c == "+":
            self.add_token("add")
        elif c == "-":
            self.add_token("subtract")
        elif c == "*":
            if self.peek() == "*":
                self.add_token("exp")
            else:
                self.add_token("multiply")
        elif c == "/":
            self.add_token("div")
        elif c == "%":
            self.add_token("mod")
        elif c == '"':
            self.string()
        elif c == ' ':
            pass
        elif c == '\t':
            pass
        elif c == '\r':
            pass
        elif c == '\n':
            self.line+=1
        else:
            if self.is_digit(c):
                self.number()
            elif self.is_alpha(c):
                self.identifier()
            else:
                # error
                pass
    def is_alpha(self, char):
        return not self.is_digit(char) and not char in {
            ":","+","-","*","/","%","\n","\t"," ","\r","[","]","(",")"}
    def is_alphanumeric(self, char):
        return self.is_alpha(char) or self.is_digit(char)
    def identifier(self):
        while self.is_alphanumeric(self.peek()):
            self.advance()
        t = Token()
        t.literal = self.source[self.start:self.current].lower()
        if t.literal in Token.reserved:
            t.type = t.literal
        else:
            t.type = "identifier"
        t.line = self.line
        self.tokens.append(t)
    def is_digit(self, char):
        return ord(char) < 58 and ord(char) > 47
    def number(self):
        while self.is_digit(self.peek()):
            self.advance()
        if self.peek() == "." and self.is_digit(self.peek_next()):
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()
        t = Token()
        t.type = "number"
        t.literal = self.source[self.start:self.current]
        t.val = float(t.literal)
        t.line = self.line
        self.tokens.append(t)
    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line+=1
            self.advance()
        if self.is_at_end():
            # error
            return
        self.advance()
        literal = self.source[self.start+1: self.current-1]
        t = Token()
        t.type = "text"
        t.literal = literal
        t.line = self.line
        self.tokens.append(t)
    def peek(self):
        if self.is_at_end():
            return "\0"
        return self.source[self.current]
    def peek_next(self):
        if self.current+1 >= len(self.source):
            return '\0'
        return self.source[self.current+1]
    def add_token(self, type):
        t = Token()
        t.type = type
        t.line = self.line
        t.literal = self.source[self.start:self.current]
        self.tokens.append(t)
    def is_at_end(self):
        return self.current >= len(self.source)
    def advance(self):
        self.current+=1
        return self.source[self.current-1]

class Parser():
    def __init__(self):
        self.children = []
        self.characters = {}
        self.keywords = {}
        self.curent = 0
        self.tokens = []
    def add_file(self, fname):
        f = open(fname)
        self.add_source(f.read())
    def add_source(self, source):
        t = Scanner()
        self.tokens = t.tokenize(source)
        '''for token in self.tokens:
            print(token)'''
        # ignore tokens up until first scene
        while self.peek().type != "scene":
            self.advance()
        while not self.is_at_end():
            stmt = self.outer_stmt()
            self.children.append(stmt)
        print(self.children)

    def outer_stmt(self):
        if self.match("l_bracket"):
            t = self.advance()
            if not self.is_inner():
                self.error(t, "Invalid keyword in inner statement")
            stmt = self.statement(t.type)
            self.consume("r_bracket", "Expected ']' at end of statement.")
            return stmt
        if self.is_outer():
            t = self.advance()
            self.consume("colon",  "Expected ':' at end of statement.")
            return self.statement(t.type)
        else:
            self.error(t, "Invalid keyword in outer statement")
            
    '''
    top_stmt = {"scene","clip","option"}
    bottom_stmt = {"if","set"}
    misc_stmt = {"location","music","sound","load","jump"}
    '''

    def is_outer(self):
        t = self.peek().type
        return t in Token.top_stmt or t in Token.misc_stmt

    def is_inner(self):
        t = self.peek().type
        return t in Token.bottom_stmt or t in Token.misc_stmt

    def statement(self, keyword):
        if keyword == "scene":
            return self.scene()
        elif keyword == "clip":
            return self.clip()
        elif keyword == "option":
            return self.option()
        elif keyword == "if":
            return self.if_stmt()
        elif keyword == "set":
            return self.set_stmt()
        else:
            return {"type": keyword, "arg": self.advance()}
        

    def scene(self):
        pass

    def clip(self):
        pass

    def option(self):
        pass

    def if_stmt(self):
        pass

    def set_stmt(self):
        pass

    def match(self, *args):
        for arg in args:
            if self.check(arg):
                self.advance()
                return True
        return False
    def check(self, type):
        if self.is_at_end():
            return False
        return self.peek().type == type
    def advance(self):
        if not self.is_at_end():
            self.curent+=1
        return self.previous()
    def is_at_end(self):
        return self.peek().type == "eof"
    def peek(self):
        return self.tokens[self.curent]
    def previous(self):
        return self.tokens[self.curent-1]
    def consume(self, type, message):
        if self.check(type):
            return self.advance()
        self.error(self.peek(), message)
    def error(self, token, message):
        if token.type == "eof":
            raise Exception(str(token.line) + " at end " + message)
        raise Exception("Error on line "+ str(token.line) + " at '" + token.literal + "' " + message)

if __name__ == "__main__":
    '''args = sys.argv[1:]
    if len(args) > 1:
        out_fname = args[0]
        in_fname = args[1]'''
    p = Parser()
    p.add_file("test.pro")