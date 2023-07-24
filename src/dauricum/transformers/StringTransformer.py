import ast, random, string, math
from dauricum.logger import Logger

"""

StringTranformer - obscures strings

"yummy!" -> (lambda: "".join((lambda: ...)(), (lambda: ...)(), (lambda: ...)()...))()

"""

class StringController:
    def obscure_string(string):
        obscured = []
        elts = []
        
        for char in string:
            key = random.randint(100000000000000, 9999999999999999999999999)
            obscured.append([ord(char) ^ key, key])
        
        for obscured_val in obscured:
            elts.append( ast.Call(
                        func=ast.Lambda(
                            args=ast.arguments(
                                posonlyargs=[],
                                args=[],
                                kwonlyargs=[],
                                kw_defaults=[],
                                defaults=[]),
                            body=ast.Call(
                                func=ast.Name(id='chr', ctx=ast.Load()),
                                args=[
                                    ast.BinOp(
                                        left=ast.Constant(value=obscured_val[0]),
                                        op=ast.BitXor(),
                                        right=ast.Constant(value=obscured_val[1]))],
                                keywords=[])),
                              args=[],
                              keywords=[]) )
        
        obsucred_tree = ast.Call(
            func=ast.Lambda(
               args=ast.arguments(
                  posonlyargs=[],
                  args=[],
                  kwonlyargs=[],
                  kw_defaults=[],
                  defaults=[]),
               body=ast.Call(
                  func=ast.Attribute(
                     value=ast.Constant(value=''),
                     attr='join',
                     ctx=ast.Load()),
                  args=[
                     ast.List(
                        elts=elts,
                        ctx=ast.Load())],
                  keywords=[])),
            args=[],
            keywords=[])
        
        return obsucred_tree
    
    def instantiate_parents(tree):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node

class StringTransformer:
    proceeded = 0
    
    def __init__(self, tree):
        Logger.logger.name = __class__.__name__
        self.tree = tree
    def __init__(self):
        Logger.logger.name = __class__.__name__
        self.tree = None
        
    def setTree(self, tree):
        self.tree = tree
    
    def proceed(self):
        Logger.logger.info(f"Transforming {self.__class__.__name__}...")
        
        StringController.instantiate_parents(self.tree)
        
        newTree = StringTransformer.StringTransformer().visit(self.tree)
        ast.fix_missing_locations(newTree)
        
        Logger.logger.info(f"Transformed Strings: {StringTransformer.proceeded}")
        
        return newTree
    
    class StringTransformer(ast.NodeTransformer):
        def visit_Constant(self, node: ast.Constant):
            if (not isinstance(node.value, str)): return node
            if (isinstance(node.parent, ast.JoinedStr)): return node
            
            node = StringController.obscure_string(node.value)
            
            StringTransformer.proceeded += 1
            
            return node