import ast, random, string
from dauricum.logger import Logger

" Traps pydecompyle3's eval "

class MemoryController:
    def getName():
        name = ''.join(random.choice(string.ascii_lowercase + (string.digits * 2)) for i in range(4, 24))
        
        while (name[0].isdigit()):
            name = ''.join(random.choice(string.ascii_lowercase + (string.digits * 2)) for i in range(4, 24))
        
        return name
    def getNode():
        return ast.Assign(targets=[ast.Name(id=MemoryController.getName(), ctx=ast.Store())], value=ast.List(elts=[ast.BinOp(left=ast.Constant(value=''), op=ast.Mult(), right=ast.Constant(value=random.randint(40480, 60960)))], ctx=ast.Load()))

class MemoryTransformer:
    proceeded_ops = 0
    
    def __init__(self, tree):
        Logger.logger.name = __class__.__name__
        self.tree = tree
    
    def proceed(self):
        Logger.logger.info(f"Transforming {self.__class__.__name__}...")
        
        self.tree.body.insert(0, MemoryController.getNode())
        self.tree.body.insert(0, ast.Expr(value=ast.Call(func=ast.Attribute(value=ast.Name(id='sys', ctx=ast.Load()), attr='set_int_max_str_digits', ctx=ast.Load()), args=[ast.Constant(value=60961)], keywords=[])))
        self.tree.body.insert(0, ast.Import(names=[ast.alias(name='sys')]))
        
        newTree = MemoryTransformer.MemoryTransformer().visit(self.tree)
        ast.fix_missing_locations(newTree)
        
        Logger.logger.info(f"Transformed If-statements: {MemoryTransformer.proceeded_ops}")
        
        return newTree
    
    class MemoryTransformer(ast.NodeTransformer):
        def visit_If(self, node: ast.If):
            node.body.insert(0, MemoryController.getNode())
            
            MemoryTransformer.proceeded_ops += 1
            return node