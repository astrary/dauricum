import ast, string, random, math
from dauricum.logger import Logger

class MBAExprPattern:
    def __init__(self, transformer):
        self.transformer = transformer

class PatternAdd(ast.NodeTransformer):
    def visit_BinOp(self, node: ast.BinOp):
        MBAExprTransformer.proceeded_binops += 1
        if (not isinstance(node.op, ast.Add)): return node
        if (MBAExprController.isInvalid(node)): return node
        for ch in ast.iter_child_nodes(node):
            if (isinstance(ch, ast.Call)):
                return node
        
        lValue = MBAExprController.wrapValue(node.left)
        rValue = MBAExprController.wrapValue(node.right)
        
        node = ast.BinOp(
            left=ast.UnaryOp(
               op=ast.Invert(),
               operand=ast.BinOp(
                  left=ast.BinOp(
                     left=ast.UnaryOp(
                        op=ast.Invert(),
                        operand=ast.BinOp(
                           left=lValue,
                           op=ast.BitXor(),
                           right=rValue)),
                     op=ast.Sub(),
                     right=ast.UnaryOp(
                        op=ast.Invert(),
                        operand=ast.BinOp(
                           left=rValue,
                           op=ast.BitXor(),
                           right=lValue))),
                  op=ast.Mult(),
                  right=ast.BinOp(
                     left=ast.UnaryOp(
                        op=ast.USub(),
                        operand=lValue),
                     op=ast.BitXor(),
                     right=ast.UnaryOp(
                        op=ast.Invert(),
                        operand=rValue)))),
            op=ast.Sub(),
            right=ast.UnaryOp(
               op=ast.Invert(),
               operand=ast.BinOp(
                  left=ast.BinOp(
                     left=ast.BinOp(
                        left=ast.BinOp(
                           left=ast.BinOp(
                              left=lValue,
                              op=ast.BitXor(),
                              right=rValue),
                           op=ast.Add(),
                           right=ast.BinOp(
                              left=ast.Constant(value=2),
                              op=ast.Mult(),
                              right=ast.BinOp(
                                 left=lValue,
                                 op=ast.BitAnd(),
                                 right=rValue))),
                        op=ast.Sub(),
                        right=rValue),
                     op=ast.BitXor(),
                     right=ast.BinOp(
                        left=rValue,
                        op=ast.Mod(),
                        right=lValue)),
                  op=ast.Add(),
                  right=ast.BinOp(
                     left=ast.Constant(value=2),
                     op=ast.Mult(),
                     right=ast.BinOp(
                        left=lValue,
                        op=ast.BitAnd(),
                        right=rValue)))))
        
        return node
class PatternMult(ast.NodeTransformer):
    def visit_BinOp(self, node: ast.BinOp):
        if (not isinstance(node.op, ast.Mult)): return node
        if (MBAExprController.isInvalid(node)): return node
        for ch in ast.iter_child_nodes(node):
            if (isinstance(ch, ast.Call)):
                return node
        MBAExprTransformer.proceeded_binops += 1
        
        lValue = MBAExprController.wrapValue(node.left)
        rValue = MBAExprController.wrapValue(node.right)
        
        node = ast.BinOp(
            left=ast.BinOp(
               left=ast.BinOp(
                  left=ast.BinOp(
                     left=lValue,
                     op=ast.Mult(),
                     right=rValue),
                  op=ast.BitOr(),
                  right=ast.BinOp(
                     left=rValue,
                     op=ast.Mult(),
                     right=lValue)),
               op=ast.Sub(),
               right=ast.BinOp(
                  left=ast.BinOp(
                     left=lValue,
                     op=ast.Mult(),
                     right=rValue),
                  op=ast.BitAnd(),
                  right=ast.BinOp(
                     left=rValue,
                     op=ast.Mult(),
                     right=lValue))),
            op=ast.Add(),
            right=ast.BinOp(
               left=ast.BinOp(
                  left=ast.BinOp(
                     left=ast.BinOp(
                        left=ast.BinOp(
                           left=ast.BinOp(
                              left=lValue,
                              op=ast.Sub(),
                              right=ast.Constant(value=3)),
                           op=ast.Pow(),
                           right=ast.Constant(value=2)),
                        op=ast.Sub(),
                        right=ast.BinOp(
                           left=lValue,
                           op=ast.Pow(),
                           right=ast.Constant(value=2))),
                     op=ast.Add(),
                     right=ast.BinOp(
                        left=ast.Constant(value=7),
                        op=ast.Mult(),
                        right=lValue)),
                  op=ast.Sub(),
                  right=ast.Constant(value=9)),
               op=ast.Mult(),
               right=ast.BinOp(
                  left=ast.BinOp(
                     left=ast.BinOp(
                        left=ast.BinOp(
                           left=ast.BinOp(
                              left=rValue,
                              op=ast.Sub(),
                              right=ast.Constant(value=3)),
                           op=ast.Pow(),
                           right=ast.Constant(value=2)),
                        op=ast.Sub(),
                        right=ast.BinOp(
                           left=rValue,
                           op=ast.Pow(),
                           right=ast.Constant(value=2))),
                     op=ast.Add(),
                     right=ast.BinOp(
                        left=ast.Constant(value=7),
                        op=ast.Mult(),
                        right=rValue)),
                  op=ast.Sub(),
                  right=ast.Constant(value=9))))
        
        return node
class PatternSub(ast.NodeTransformer):
    def visit_BinOp(self, node: ast.BinOp):
        if (not isinstance(node.op, ast.Sub)): return node
        if (MBAExprController.isInvalid(node)): return node
        for ch in ast.iter_child_nodes(node):
            if (isinstance(ch, ast.Call)):
                return node
        MBAExprTransformer.proceeded_binops += 1
        
        lValue = MBAExprController.wrapValue(node.left)
        rValue = MBAExprController.wrapValue(node.right)
        
        node = ast.UnaryOp(
            op=ast.USub(),
            operand=ast.BinOp(
               left=ast.BinOp(
                  left=ast.UnaryOp(
                     op=ast.USub(),
                     operand=ast.BinOp(
                        left=lValue,
                        op=ast.BitXor(),
                        right=ast.UnaryOp(
                           op=ast.USub(),
                           operand=rValue))),
                  op=ast.Sub(),
                  right=ast.BinOp(
                     left=ast.BinOp(
                        left=lValue,
                        op=ast.Add(),
                        right=ast.UnaryOp(
                           op=ast.USub(),
                           operand=rValue)),
                     op=ast.Sub(),
                     right=ast.BinOp(
                        left=ast.BinOp(
                           left=ast.BinOp(
                              left=lValue,
                              op=ast.Add(),
                              right=ast.UnaryOp(
                                 op=ast.USub(),
                                 operand=rValue)),
                           op=ast.Add(),
                           right=ast.Constant(value=1)),
                        op=ast.Add(),
                        right=ast.BinOp(
                           left=ast.UnaryOp(
                              op=ast.Invert(),
                              operand=lValue),
                           op=ast.BitOr(),
                           right=ast.UnaryOp(
                              op=ast.Invert(),
                              operand=ast.UnaryOp(
                                 op=ast.USub(),
                                 operand=rValue)))))),
               op=ast.Sub(),
               right=ast.BinOp(
                  left=ast.BinOp(
                     left=lValue,
                     op=ast.Add(),
                     right=ast.UnaryOp(
                        op=ast.USub(),
                        operand=rValue)),
                  op=ast.Sub(),
                  right=ast.BinOp(
                     left=ast.BinOp(
                        left=ast.BinOp(
                           left=lValue,
                           op=ast.Add(),
                           right=ast.UnaryOp(
                              op=ast.USub(),
                              operand=rValue)),
                        op=ast.Add(),
                        right=ast.Constant(value=1)),
                     op=ast.Add(),
                     right=ast.BinOp(
                        left=ast.UnaryOp(
                           op=ast.Invert(),
                           operand=lValue),
                        op=ast.BitOr(),
                        right=ast.UnaryOp(
                           op=ast.Invert(),
                           operand=ast.UnaryOp(
                              op=ast.USub(),
                              operand=rValue)))))))
        
        return node
class PatternBitXor(ast.NodeTransformer):
    def visit_BinOp(self, node: ast.BinOp):
        if (not isinstance(node.op, ast.BitXor)): return node
        if (MBAExprController.isInvalid(node)): return node
        for ch in ast.iter_child_nodes(node):
            if (isinstance(ch, ast.Call)):
                return node
        MBAExprTransformer.proceeded_binops += 1
        
        lValue = MBAExprController.wrapValue(node.left)
        rValue = MBAExprController.wrapValue(node.right)
        
        node = ast.BinOp(
            left=ast.BinOp(
               left=ast.BinOp(
                  left=ast.BinOp(
                     left=ast.BinOp(
                        left=lValue,
                        op=ast.BitAnd(),
                        right=rValue),
                     op=ast.Add(),
                     right=ast.BinOp(
                        left=lValue,
                        op=ast.BitOr(),
                        right=rValue)),
                  op=ast.Add(),
                  right=ast.Constant(value=1)),
               op=ast.Add(),
               right=ast.BinOp(
                  left=ast.UnaryOp(
                     op=ast.Invert(),
                     operand=lValue),
                  op=ast.BitOr(),
                  right=ast.UnaryOp(
                     op=ast.Invert(),
                     operand=rValue))),
            op=ast.Sub(),
            right=ast.BinOp(
               left=ast.BinOp(
                  left=ast.BinOp(
                     left=lValue,
                     op=ast.BitAnd(),
                     right=rValue),
                  op=ast.Add(),
                  right=ast.BinOp(
                     left=lValue,
                     op=ast.BitOr(),
                     right=rValue)),
               op=ast.Sub(),
               right=ast.BinOp(
                  left=ast.BinOp(
                     left=ast.BinOp(
                        left=ast.BinOp(
                           left=lValue,
                           op=ast.BitAnd(),
                           right=rValue),
                        op=ast.Add(),
                        right=ast.BinOp(
                           left=lValue,
                           op=ast.BitOr(),
                           right=rValue)),
                     op=ast.Add(),
                     right=ast.Constant(value=1)),
                  op=ast.Add(),
                  right=ast.BinOp(
                     left=ast.UnaryOp(
                        op=ast.Invert(),
                        operand=lValue),
                     op=ast.BitOr(),
                     right=ast.UnaryOp(
                        op=ast.Invert(),
                        operand=rValue)))))
        
        return node
class PatternNum(ast.NodeTransformer):
    def visit_Num(self, node: ast.Num):
        for ch in ast.iter_child_nodes(node):
            if (isinstance(ch, ast.Call)):
                return node
        if (isinstance(node.parent, ast.Call)):
            node = MBAExprController.wrapConst(node)
        
        return node

class MBAExprPatterns:
    def add(self, pattern):
        self.patterns.append(pattern)
    
    def __init__(self):
        self.patterns = []
        
        self.add( MBAExprPattern(PatternNum) )
        self.add( MBAExprPattern(PatternAdd) )
        self.add( MBAExprPattern(PatternMult) )
        self.add( MBAExprPattern(PatternSub) )
        self.add( MBAExprPattern(PatternBitXor) )

class MBAExprController:
    def getName():
        name = ''.join(random.choice(string.ascii_lowercase + (string.digits * 2)) for i in range(4, 24))
        
        while (name[0].isdigit()):
            name = ''.join(random.choice(string.ascii_lowercase + (string.digits * 2)) for i in range(4, 24))
        
        return name
    def instantiateParents(tree):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
    def isInvalid(binOp: ast.BinOp):
        if (isinstance(binOp.left, ast.Constant) and isinstance(binOp.right, ast.Constant)): 
            return isinstance(binOp.left.value, str) or isinstance(binOp.right.value, str)
        return True
        
    def wrapValue(wrap_value):
        if (not MBAExprTransformer.wrapping_enabled): return wrap_value
        
        if (not isinstance(wrap_value, ast.Constant)): return wrap_value
        if (not isinstance(wrap_value.value, int)): return wrap_value
        key = random.randint(10, 100)
        obf_value = wrap_value.value ^ key
        
        return ast.BinOp(
            left=ast.BinOp(
               left=ast.BinOp(
                  left=ast.BinOp(
                     left=ast.Constant(value=obf_value),
                     op=ast.Add(),
                     right=ast.Constant(value=key)),
                  op=ast.Add(),
                  right=ast.Constant(value=1)),
               op=ast.Add(),
               right=ast.BinOp(
                  left=ast.UnaryOp(
                     op=ast.Invert(),
                     operand=ast.Constant(value=obf_value)),
                  op=ast.BitOr(),
                  right=ast.UnaryOp(
                     op=ast.Invert(),
                     operand=ast.Constant(value=key)))),
            op=ast.Sub(),
            right=ast.BinOp(
               left=ast.BinOp(
                  left=ast.Constant(value=obf_value),
                  op=ast.Add(),
                  right=ast.Constant(value=key)),
               op=ast.Sub(),
               right=ast.BinOp(
                  left=ast.Constant(value=obf_value),
                  op=ast.BitOr(),
                  right=ast.Constant(value=key))))
    def wrapConst(wrap_value):
        if (not isinstance(wrap_value, ast.Constant)): return wrap_value
        if (not isinstance(wrap_value.value, int)): return wrap_value
        key = random.randint(10, 100)
        obf_value = wrap_value.value ^ key
        
        return ast.BinOp(
            left=ast.BinOp(
               left=ast.BinOp(
                  left=ast.BinOp(
                     left=ast.Constant(value=obf_value),
                     op=ast.Add(),
                     right=ast.Constant(value=key)),
                  op=ast.Add(),
                  right=ast.Constant(value=1)),
               op=ast.Add(),
               right=ast.BinOp(
                  left=ast.UnaryOp(
                     op=ast.Invert(),
                     operand=ast.Constant(value=obf_value)),
                  op=ast.BitOr(),
                  right=ast.UnaryOp(
                     op=ast.Invert(),
                     operand=ast.Constant(value=key)))),
            op=ast.Sub(),
            right=ast.BinOp(
               left=ast.BinOp(
                  left=ast.Constant(value=obf_value),
                  op=ast.Add(),
                  right=ast.Constant(value=key)),
               op=ast.Sub(),
               right=ast.BinOp(
                  left=ast.Constant(value=obf_value),
                  op=ast.BitOr(),
                  right=ast.Constant(value=key))))
        

class MBAExprTransformer:
      proceeded_binops = 0
      wrapping_enabled = False
      
      def __init__(self, wrapping_enabled):
         Logger.logger.name = __class__.__name__
         self.tree = None
         MBAExprTransformer.wrapping_enabled = wrapping_enabled
         
         self.patterns = MBAExprPatterns()
         
      def setTree(self, tree):
         self.tree = tree
      
      def proceed(self):
         if (not MBAExprTransformer.wrapping_enabled):
            Logger.logger.warn(f"Number Wrapping is disabled.")
         
         Logger.logger.info(f"Transforming {self.__class__.__name__}...")
         
         for pattern in self.patterns.patterns:
               MBAExprController.instantiateParents(self.tree)
               self.tree = pattern.transformer().visit(self.tree)
               ast.fix_missing_locations(self.tree)
         
         Logger.logger.info(f"Transformed BinOps: {MBAExprTransformer.proceeded_binops}")
         
         return self.tree