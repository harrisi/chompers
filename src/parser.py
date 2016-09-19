import string

class InputStream(object):
    def __init__(self, input_stream):
        self.pos = 0
        self.line = 1
        self.col = 0
        self.input_stream = input_stream

    def next(self):
        ch = self.input_stream[self.pos]
        self.pos += 1
        if (ch == '\n'):
            self.line += 1
            self.col = 0
        else:
            self.col += 1
        return ch

    def peek(self):
        return self.input_stream[self.pos]

    def eof(self):
        return self.peek() == ''

    def croak(self, msg):
        raise Exception(msg + " (" + str(self.line) + ":" + str(self.col) + ')')

def parseNum(n):
    try:
        return int(n, base = 0)
    except:
        try:
            return float(n)
        except:
            return None # bad!

class TokenStream(object):
    def __init__(self, input_stream):
        self.input_stream = input_stream
        self.current = None
        self.keywords = 'if then else lambda true false'

    def is_keyword(self, tok):
        return tok in self.keywords

    def is_digit(self, ch):
        return parseNum(ch) is not None

    def is_id_start(self, ch):
        return ch in string.letters + '_'

    def is_id(self, ch):
        return self.is_id_start(ch) or ch in string.digits + '?!-<>=`'

    def is_op_char(self, ch):
        return ch in '+-*/%=&|<>!'

    def is_punc(self, ch):
        return ch in ',;:(){}[]'

    def is_whitespace(self, ch):
        return ch in string.whitespace

    def read_while(self, predicate):
        s = ''
        while (not self.input_stream.eof() and
                predicate(self.input_stream.peek())):
            s += self.input_stream.next()
        return s

    def read_number(self): # needed?
        has_dot = False
        def pred(ch):
            if ch == '.':
                if has_dot:
                    return false
                has_dot = True
                return True
            return self.is_digit(ch)
        number = self.read_while(pred)
        return {'_type': 'num', '_value': parseNum(number)}

    def read_ident(self):
        ident = self.read_while(self.is_id)
        return {'_type': "kw" if self.is_keyword(ident) else "var",
                '_value': ident}

    def read_escaped(self, end):
        escaped = False
        s = ''
        self.input_stream.next()
        while not self.input_stream.next():
            ch = self.input_stream.next()
            if escaped:
                s += ch
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == end:
                break
            else:
                s += ch
        return s

    def read_string(self):
        return {'_type': 'str', '_value': self.read_escaped('"')}

    def skip_comment(self):
        self.read_while(lambda ch: ch != '\n')
        self.input_stream.next()

    def read_next(self):
        self.read_while(self.is_whitespace)
        if self.input_stream.eof():
            return None
        ch = self.input_stream.peek()
        if ch == '#':
            self.skip_comment()
            return self.read_next()
        if ch == '"':
            return self.read_string()
        if self.is_digit(ch):
            return self.read_number()
        if self.is_punc(ch):
            return {'_type': 'punc', '_value': self.input_stream.next()}
        if self.is_id_start(ch):
            return self.read_ident()
        if self.is_op_char(ch):
            return {'_type': 'op', '_value': self.read_while(self.is_op_char)}
        self.input_stream.croak("Can't handle character: " + str(ch))

    def peek(self):
        if self.current is None:
            self.current = self.read_next()
        return self.current

    def next(self):
        tok = self.current
        self.current = None
        if tok is None:
            return self.read_next()
        return tok

    def eof(self):
        return self.peek() is None
