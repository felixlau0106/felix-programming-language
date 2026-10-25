

class ASTNode:
    pass

class Number(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"NumberNode({self.value})"

class String(ASTNode):
    def __init__(self, value):
        self.value = value
    
    def __repr__(self):
        return f"StringNode({self.value!r})"

class Boolean(ASTNode):
    def __init__(self, value):
        self.value = value
    
    def __repr__(self):
        return f"BooleanNode({self.value})"

class List(ASTNode):
    def __init__(self, elements):
        self.elements = elements

    def __repr__(self):
        return f"List({self.elements})"

class Subscript(ASTNode):
    def __init__(self, obj, index):
        self.obj = obj
        self.index = index

    def __repr__(self):
        return f"Subscript({self.obj}, {self.index})"

class Variable(ASTNode):
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return f"VariableNode({self.name!r})"

class TypedName(ASTNode):
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __repr__(self):
        return f"TypedName({self.name}, {self.type})"

class UnaryOp(ASTNode):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

    def __repr__(self):
        return f"UnaryOp({self.op!r}, {self.operand!r})"

class BinaryOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.left!r}, {self.op!r}, {self.right!r})"
        # Suggested by Gemini: use !r to show '+' instead of +
        # Ask Groky `why`` later

class Assign(ASTNode):
    def __init__(self,left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Assign({self.left!r}, {self.right})"


class If(ASTNode):
    def __init__(self, cond, body, orelse=None):
        self.cond = cond
        self.body = body
        self.orelse = orelse

    def __repr__(self):
        if self.orelse:
            return f"If({self.cond!r},{self.body!r},{self.orelse!r})"
        return f"If({self.cond!r},{self.body!r})"

class While(ASTNode):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def __repr__(self):
        return f"While({self.cond!r},{self.body!r})"

class Def(ASTNode):
    def __init__(self, name, params, body, return_type):
        self.name = name
        self.params = params
        self.body = body
        self.return_type = return_type

    def __repr__(self):
        return f"Def({self.name!r}, {self.params!r}, {self.return_type}, {self.body!r})"

class Return(ASTNode):
    def __init__(self, value=None):
        self.value = value

    def __repr__(self):
        return f"Return({self.value!r})"
    
class Call(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"Call({self.name!r}, {self.args!r})"

class Get(ASTNode):
    def __init__(self, obj, name):
        self.obj = obj
        self.name = name

    def __repr__(self):
        return f"Get({self.obj!r}, {self.name!r})" 

class ErrorNode(ASTNode):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return f"ErrorNode({self.message!r})"

if __name__ == "__main__":
    print("Felix's AST Nodes")