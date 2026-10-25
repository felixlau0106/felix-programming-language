from lexer import TokenType
from ast_nodes import Number, String, Boolean, Variable, UnaryOp, BinaryOp, Call, ErrorNode, Assign, If, While, Def, Return, List, Get, Subscript, TypedName

class Parser:
    def __init__(self, tokens, source):
        self.diagnostics = []
        self.source = source
        self.tokens = tokens
        self.current = 0

    # We don't peek at position of EOF so no need to add a guard like lexer
    def peek(self):
        return self.tokens[self.current]

    # Eat one token, then point `self.current` to the next one, and return the eaten token
    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.tokens[self.current - 1]

    # Check if the current token is of the given type. If it is, return True. Otherwise, return False.
    def check(self, *types) -> bool:
        if self.is_at_end():
            return False
        for t in types:
            if self.peek().type == t:
                return True
        return False

    # If the current token is of the given type(s), Eat it and return True. Otherwise, return False.
    def match(self, *types) -> bool:
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    # Meaner sibling of match(). “this must be here. give it to me or I scream.”
    # It is used when something is required. Like the grammar promised a closer.
    def consume(self, type, msg, line, column, suggestion=None):
        if self.check(type):
            return self.advance()
        else:
            self.diagnostics.append((msg, line, column, suggestion))
            return ErrorNode(msg)
        
    # Return True if the current token is EOF, otherwise return False.
    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def skip_seps(self):
        while self.match(TokenType.SEMICOLON, TokenType.NEWLINE):
            pass

    def print_diagnostics(self):
            RED = "\033[91m"
            YELLOW = "\033[93m"
            GRAY = "\033[90m"
            RESET = "\033[0m"
            
            for diag in self.diagnostics:
                message, line, column, suggestion = diag
                line_number_string = str(line)
                margin_width = max(3, len(line_number_string))
                margin = " " * margin_width
                print(f"{RED}Error[Line {line}, Col {column}]: {message}{RESET}")
                print(f"{GRAY}{margin} |{RESET}")
                
                padded_line = line_number_string.rjust(margin_width)
                source_code = self.source.splitlines()[line - 1]
                print(f"{GRAY}{padded_line} |{RESET} {source_code}")
                print(f"{GRAY}{margin} |{RESET} {RED}" + " " * (column - 1) + f"^{RESET}")
                if suggestion:
                    print(f"{GRAY}{margin} |{RESET}")
                    print(f"{YELLOW}{margin} = Help: {suggestion}{RESET}")
                print(f"\n{GRAY}" + "─" * 60 + f"{RESET}\n")


    # A FUCKING INSANE Ladder!
    #   parser               (call expression())
    #   | - expression          (calls or_expr() to handle or expressions)
    #       | - or_expr            (calls and_expr() to handle and expressions)
    #           | - and_expr          (calls equality() to handle equality expressions)
    #               | - equality         (calls comparison() to handle comparison expressions)
    #                   | - comparison      (calls term() to handle addition and subtraction)
    #                       | - term           (calls factor() to handle multiplication, division, and modulus)
    #                           | - factor        (calls unary() to handle unary operations)
    #                               | - unary        (calls call() to handle function calls)
    #                                   | - call        (calls primary() to handle primary expressions)
    #                                       | - primary    (this returns the actual nodes like Number, String, Boolean, Variable, etc.)
    
    
    def parse(self):
        nodes = []
        while not self.is_at_end():
            self.skip_seps() # if we face a semicolon or newline, match() eats it then we append the expression() node to the list.
            if self.is_at_end(): # This avoid adding a None node at the end!
                break # not running expression() if we are at the end, because expression() will return None and we don't want that.
            nodes.append(self.statement())
        return nodes

    def statement(self):
        if self.match(TokenType.IF):
            return self.if_statement()
        elif self.match(TokenType.ELIF):
            tok = self.tokens[self.current - 1]
            self.diagnostics.append((f"Parser Error: elif without if or syntax error within the if statement block", tok.line, tok.column, None))
            return ErrorNode(f"Parser Error: unexpected token {tok.lexeme}")
        elif self.match(TokenType.ELSE):
            tok = self.tokens[self.current - 1]  
            self.diagnostics.append((f"Parser Error: else without if or syntax error within the if statement block", tok.line, tok.column, None))
            return ErrorNode(f"Parser Error: unexpected token {tok.lexeme}")
        elif self.match(TokenType.WHILE):
            return self.while_statement() # a while statement block can live inside an if statement block
        elif self.match(TokenType.DEF):
            return self.def_statement()
        elif self.match(TokenType.RETURN):
            return self.return_statement()
        
        left = self.expression()
        while self.match(TokenType.EQUAL):
            op = self.tokens[self.current - 1]
            right = self.statement()
            left = Assign(left, right)
        return left

    def return_statement(self):
        if self.check(TokenType.NEWLINE, TokenType.END, TokenType.SEMICOLON):
            return Return()
        rvalue = self.expression()
        return Return(rvalue)

    def def_statement(self):
        param = []
        body = []
        opener = self.tokens[self.current - 1] # Because statement() ate the while
        name = self.primary()
        self.consume(TokenType.LPAREN, "Parser Error: inappropriate def statement, expected ( after function name", opener.line, opener.column, "Try add back a ()")
        if not self.check(TokenType.RPAREN):  # Check if there are arguments
            opener = self.tokens[self.current]
            typed_name = self.primary()
            if not isinstance(typed_name, TypedName):
                self.diagnostics.append(("Parser Error: Invalid param, expected a typed name", opener.line, opener.column, "Try use typed name like: x: int or my_list: list"))
                param.append(ErrorNode("Invalid param, expected TypedName"))
            else:
                param.append(typed_name)
            while self.match(TokenType.COMMA):
                opener = self.tokens[self.current]
                if self.check(TokenType.RPAREN):
                    self.diagnostics.append(("Parser Error: Extra comma after param", opener.line, opener.column - 1, "Try remove the extra comma")) # match ate the comma and we are at RPAREN, meaning col-1 is the eaten comma
                    break
                typed_name = self.primary()
                if not isinstance(typed_name, TypedName):
                    self.diagnostics.append(("Parser Error: Invalid param, expected a typed name", opener.line, opener.column, "Try use typed name like: x: int or my_list: list"))
                    param.append(ErrorNode("Invalid param, expected TypedName"))
                else:
                    param.append(typed_name)

        opener = self.tokens[self.current] # If RPAREN is missing, we are at `:` or return type if ':' is also missing. so col-1 to get the position of caret
        con = self.consume(TokenType.RPAREN, "Parser Error: inappropriate def statement, expected ) after param", opener.line, opener.column-1, "Try add back a ) after param")
        
        if not isinstance(con, ErrorNode): # if RPAREN is already missing, there is no point to ask for the colon after RPAREN
            opener = self.tokens[self.current - 1] # If RPAREN was eaten and colon is missing, we are at return type or newline if return type is missing. So current - 1 to point at the ':'
            self.consume(TokenType.COLON, "Parser Error: inappropriate def statement, expected : after )", opener.line, opener.column, "Try add back a : after )")
            
        rtype = self.expression() # This SHOULD be a normal Variable
        if not isinstance(rtype, Variable): # If NOT
            opener = self.tokens[self.current - 1]
            self.diagnostics.append(("Parser Error: Missing return type", opener.line, opener.column, "Try add back the return type of this function"))
            rtype = ErrorNode(f"Invalid return type: {opener.lexeme}")
        self.skip_seps() # End of the first line of def statement, skip seps

        while not (self.check(TokenType.END) or self.is_at_end()):
            body.append(self.statement())
            self.skip_seps()
        self.consume(TokenType.END, "Parser Error: def statement never ended, expected end after the def code block", opener.line, opener.column, "Try add back an end)")
        return Def(name, param, body, rtype)

    def while_statement(self):
        body = []
        opener = self.tokens[self.current - 1] # Because statement() ate the while
        cond = self.expression()
        self.consume(TokenType.COLON, "Parser Error: inappropriate while statement, expected : after condition", opener.line, opener.column, "Try add back a : after condition")
        self.skip_seps() # After an If Condition it is expected to see a new line or semicolon(if user tried to do one-liner challenge)
        while not (self.check(TokenType.END) or self.is_at_end()):
            body.append(self.statement())
            self.skip_seps()
        self.consume(TokenType.END, "Parser Error: inappropriate while statement, expected end", opener.line, opener.column, "Try close the while loop with an end")
        return While(cond, body)

    def if_statement(self):
        # Recursion for: 
        """
    line
    1       if x > 3:
    2           1
    3       elif x == 5:
    4           2
    5       else:
    6           3
        """
        # A If node is If(cond, body, orelse)
        # statement() eats IF in line 1
        # Part A call expression() to get the cond(x>3) and statement() to eat the body(line 2)
        # It is trying to create first If node (lets call it HEEHEE),
        # after skipping NEWLINE in line 2 it hits an elif in line 3, go inside Part B
        # re-call if_statement() to create a If node (lets call it HAHA) as orelse -> jump back to Part A
        # At this point HEEHEE is If('x>3",1,orelse=HAHA), it is not returned yet since it wont hit return line until HAHA is finished
        # since self.match(TokenType.ELIF) already ate the elif, call expression() to get the cond(x==5) and statement() to eat the body(line 4)
        # At this point HAHA is If('x==5',2,orelse=None), code is at the `end of Part A`
        # after skipping NEWLINE in line 4 it hits an else, go inside Part C
        # eat colon and NEWLINE, right now we are at line 6. call self.statement to get 3 at line 6, make orelse = 3
        # right now HAHA is If('x==5',2,orelse=3), return it back to HEEHEE
        # Now HEEHEE = If('x>3', 1, orelse = If('x==5', 2, orelse = 3))
        
        # Part A - no need to eat IF because caller statement() already did self.match(TokenType.IF)
        body = []
        else_body = []
        flag = self.tokens[self.current - 1] # at ELSE the opener changes for the consume() so I came up with this idea to keep the `if`
        opener = self.tokens[self.current - 1] # -1 because statement()/Part B ate the IF/ELIF
        cond = self.expression()
        self.consume(TokenType.COLON, "Parser Error: inappropriate if-statement, expected : after condition", opener.line, opener.column, "Try add back a : after condition")
        self.skip_seps() # After an If Condition it is expected to see a new line or semicolon(if user tried to do one-liner challenge)
        while not (self.check(TokenType.ELIF, TokenType.ELSE, TokenType.END) or self.is_at_end()):
            body.append(self.statement())
            self.skip_seps() # After the body(what to do) of If it is expected to see separators
        orelse = None
        # end of Part A

        # Part B
        if self.match(TokenType.ELIF):
            orelse = self.if_statement() # if hit elif run if_statement() again and treet it like a mini-if

        # Part C
        elif self.match(TokenType.ELSE):
            opener = self.tokens[self.current - 1]
            self.consume(TokenType.COLON, "Parser Error: expected : after else", opener.line, opener.column, "Try add back a : after condition")
            self.skip_seps() # After `else:` it is expected to see separators
            while not (self.check(TokenType.END) or self.is_at_end()):
                else_body.append(self.statement()) # run a final statement() to make else becoome the the last orelse of Part A
                self.skip_seps()
            orelse = else_body

        if flag.lexeme == "if": # only the original if_statement call can consume the final `end`. the recursion of elif cannot!
            self.skip_seps()
            self.consume(TokenType.END, "Parser Error: inappropriate if-statement, expected `end`", opener.line, opener.column, "Try close the if-statement with an `end`. For nested if-statements you may want to check if every `if` has a matching `end`")
        return If(cond, body, orelse) 

    def expression(self):
        return self.or_expr()

    def or_expr(self):
        left = self.and_expr()
        while self.match(TokenType.OR):
            op = self.tokens[self.current - 1] # self.match() already ate the operator
            right = self.and_expr()
            left = BinaryOp(left, op.lexeme, right)
        return left

    def and_expr(self):
        left = self.equality()
        while self.match(TokenType.AND):
            op = self.tokens[self.current - 1] # self.match() already ate the operator
            right = self.equality()
            left = BinaryOp(left, op.lexeme, right)
        return left

    def equality(self):
        left = self.comparison()
        while self.match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            op = self.tokens[self.current - 1] # self.match() already ate the operator
            right = self.comparison()
            left = BinaryOp(left, op.lexeme, right)
        return left

    def comparison(self):
        left = self.term()
        while self.match(TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL):
            op = self.tokens[self.current - 1] # self.match() already ate the operator
            right = self.term()
            left = BinaryOp(left, op.lexeme, right)
        return left

    def term(self):
        left = self.factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.tokens[self.current - 1] # self.match() already ate the operator
            right = self.factor()
            left = BinaryOp(left, op.lexeme, right)
        return left

    def factor(self):
        left = self.unary()
        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self.tokens[self.current - 1] # self.match() already ate the operator
            right = self.unary()
            left = BinaryOp(left, op.lexeme, right)
        return left

    def unary(self):
        # Recursion
        # --1
        # first unary see -, eats it then wait inner
        # second unary see -, eats it then wait for inner
        # third unary see 1, run primary() and it returns a NumberNode(1)
        # second inner is the returned NumberNode(1) so it can now return UnaryOp('-', NumberNode(1))
        # first unary see inner is that long return then finally return UnaryOp('-', UnaryOp('-', NumberNode(1)))
        # so in the case of --1, in non Python syntax:
        # 1st knows it will return ('-', y), wait for 2nd to get y
        # 2nd knows it will return y, wait for 3rd to get z
        # 3rd return z (a numbernode) -> 2nd return y = ('-', numbernode) -> 1st return ('-', y)
        if self.check(TokenType.MINUS):
            self.advance()
            inner = self.unary()
            return UnaryOp('-', inner)
        
        if self.check(TokenType.NOT):
            self.advance()
            inner = self.unary()
            return UnaryOp('not', inner)
        return self.postfix()

    def postfix(self):
        left = self.primary()
        while self.match(TokenType.LPAREN, TokenType.DOT, TokenType.LBRACKET):
            opener = self.tokens[self.current - 1] # the LPAREN token
            if opener.type == TokenType.LPAREN:
                args = []
                if self.peek().type not in [TokenType.RPAREN, TokenType.NEWLINE, TokenType.SEMICOLON, TokenType.EOF]:  # Check if there are arguments
                    args.append(self.expression())
                    while self.match(TokenType.COMMA):
                        args.append(self.expression())
                con = self.consume(TokenType.RPAREN, "Parser Error: expected ) after function call", opener.line, opener.column, "Did you forget a closing parenthesis?")
                if isinstance(con, ErrorNode):
                    return Call(left, args) # Return what we have so far!
                left = Call(left, args)
            elif opener.type == TokenType.DOT:
                name = self.consume(TokenType.IDENT, "Parser Error: expected identifier after dot", opener.line, opener.column, "Please check if this line is broken")
                if isinstance(name, ErrorNode):
                    left = Get(left, name) 
                else:
                    left = Get(left, name.lexeme)
            elif opener.type == TokenType.LBRACKET:
                if not self.check(TokenType.RBRACKET, TokenType.NEWLINE, TokenType.SEMICOLON, TokenType.EOF):
                    index = self.expression()
                    self.consume(TokenType.RBRACKET, "Parser Error: expected a closing ]", opener.line, opener.column, "Did you forget a closing bracket?")
                else:
                    self.diagnostics.append(("Parser Error: expected index after [", opener.line, opener.column, "Please put valid index between [ and ]"))
                    index = ErrorNode("Parser Error: expected index after [")
                    self.consume(TokenType.RBRACKET, "Parser Error: expected a closing ]", opener.line, opener.column, "Did you forget a closing bracket?")
                left = Subscript(left, index)
        return left

    def primary(self):
        if self.check(TokenType.NUMBER):
            tok = self.advance()
            return Number(tok.literal)
        elif self.check(TokenType.STRING):
            tok = self.advance()
            return String(tok.literal)
        elif self.check(TokenType.TRUE):
            tok = self.advance()
            return Boolean(tok.literal)
        elif self.check(TokenType.FALSE):
            tok = self.advance()
            return Boolean(tok.literal)
        elif self.check(TokenType.IDENT):
            tok = self.advance()
            if self.check(TokenType.COLON) and (self.tokens[self.current+1].type == TokenType.IDENT):
                    self.advance() # eat the COLON
                    typ = self.advance()            
                    return TypedName(Variable(tok.lexeme), Variable(typ.lexeme))
            return Variable(tok.lexeme)
        elif self.check(TokenType.LPAREN):
            opener = self.advance()  # Eat the '(' token
            node = self.expression()
            self.consume(TokenType.RPAREN, "Parser Error: expected )", opener.line, opener.column, "Did you forget a closing parenthesis?")
            return node
        elif self.check(TokenType.LBRACKET):
            opener = self.advance()
            elements = []
            while not self.check(TokenType.RBRACKET):
                elements.append(self.expression())
                if self.check(TokenType.COMMA):
                    self.advance()
            self.consume(TokenType.RBRACKET, "Parser Error: expected ]", opener.line, opener.column, "Did you forget a closing bracket?")
            return List(elements)
        elif self.check(TokenType.ERROR):
            tok = self.advance()
            #self.diagnostics.append((f"Lexer Error: {tok.lexeme}", tok.line, tok.column))
            return ErrorNode(f"Lexer Error: {tok.lexeme}")
        else:
            tok = self.advance()
            self.diagnostics.append((f"Parser Error: unexpected {tok.type}", tok.line, tok.column, None))
            return ErrorNode(f"Parser Error: unexpected token {tok.lexeme}")
        
if __name__ == "__main__":
    print_tok = 0
    from lexer import Lexer
    print("\033[93m" + "\nFelix's Compiler Debug Helper\n" + "\033[0m")
    source = """

    """
    if print_tok:
        for t in Lexer(source).scan_tokens():
            print(t)

    p = Parser(Lexer(source).scan_tokens(), source)
    nodes = p.parse()
    p.print_diagnostics()
    print("Nodes:\n")
    for exp in nodes:
        print(exp)
        print(f"\n" + "\033[90m" + "─" * 60 + f"\033[0m" + "\n")
    print("\n")
    