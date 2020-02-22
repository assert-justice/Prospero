import sys

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

class Token():
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
            self.add_token("eol")
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
        return not self.is_digit(char) and not char in {":","+","-","*","/","%","\n","\t"," ","\r","[","]"}
    def is_alphanumeric(self, char):
        return self.is_alpha(char) or self.is_digit(char)
    def identifier(self):
        while self.is_alphanumeric(self.peek()):
            self.advance()
        t = Token()
        t.literal = self.source[self.start:self.current].lower()
        if t.literal in reserved:
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

class Stmt():
    pass

class SceneStmt():
    def __init__(self, stmts):
        self.stmts = stmts

class ClipStmt():
    def __init__(self, stmts):
        self.stmts = stmts

class OptionStmt():
    def __init__(self, text, jump):
        self.jump = jump

class CondStmt():
    def __init__(self, cond_expr, then_stmts, else_stmts):
        self.cond_expr = cond_expr
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

class AssignStmt():
    def __init__(self, target, expr):
        self.target = target
        self.expr = expr

class ExprStmt():
    def __init__(self, expr):
        self.expr = expr

class CharStmt():
    def __init__(self, char, inst, args):
        self.char = char
        self.inst = inst
        self.args = args

class BinaryExpr():
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class UnaryExpr():
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

class GroupExpr():
    def __init__(self, expr):
        self.expr = expr

class PrimaryExpr():
    def __init__(self, identifier):
        self.identifier = identifier

class Parser():
    def __init__(self):
        self.scenes = {}
        self.characters = {}
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
            self.scene()
            break

    def scene(self):
        self.consume("scene", "Expected scene heading")
        self.consume("colon", "Expected ':' after scene heading")
        name = self.advance()
        self.consume("eol", "Expected end of line after scene heading")
        scene = {}
        self.scenes[name] = scene
        scene["name"] = name
        scene["clips"] = {}
        scene["stmts"] = []
        while not self.is_at_end() and not self.check("scene"):
            if self.match("l_bracket"):
                stmt = self.statement()
                self.consume("r_bracket","Expected ']' at end of statement")
                scene["stmts"].append(stmt)
            elif self.check("clip"):
                name, clip = self.clip()
                scene["clips"][name] = clip
            else:
                self.error(self.peek(), "Unexpected token")
            break

    def statement(self):
        if self.match("set"):
            ident = self.peek()
            self.consume("identifier", "Expected identifier after 'set' keyword")
            self.consume("to", "Expected 'to' keyword after identifier in set statement")
            stmt = AssignStmt(ident, self.expression())
            return stmt
        elif self.match("if"):
            cond = self.expression()
            self.consume("then", "Expected 'then' keyword after condition in if statement")
            then_stmts = []
            while True:
                then_stmts.append(self.statement())
                if not self.match("semi"):
                    break
        elif self.peek().type == "identifier":
            #if self.match("looks","enters",)
            name = self.advance()
            if not self.peek() in {"looks","enters","moves","turns"}:
                self.error(self.peek(), "Unexpected token in character command")
            inst = self.peek()
            args = []
            if self.match("looks"):
                pass
            elif self.match("enters"):
                if self.peek().type in directions:
                    args.append(self.advance())
                    if self.peek().type in stage_positions:
                        args.append(self.advance())
            elif self.match("moves"):
                pass
            elif self.match("turns"):
                pass
            stmt = CharStmt(name, inst, args)
            

    def clip(self):
        self.consume("clip", "Expected clip heading")
        self.consume("colon", "Expected ':' after clip heading")
        name = self.advance()
        self.consume("eol", "Expected end of line after clip heading")

    def expression(self):
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
        pass

if __name__ == "__main__":
    '''args = sys.argv[1:]
    if len(args) > 1:
        out_fname = args[0]
        in_fname = args[1]'''
    p = Parser()
    p.add_file("test.pro")
