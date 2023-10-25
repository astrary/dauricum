
import ast, builtins, random
from dauricum.transformers.base import Transformer
from dauricum.tools.utils import Utils
from dauricum.tools.logger import Logger

class FunctionTransformer(Transformer):
    
    def __init__(self, alphabet: str, length: int):
        self.alphabet = alphabet
        self.length = length
        
    def proceed(self, tree: ast.Module):
        Logger.logger.name = __class__.__name__
        Logger.logger.info(f"transforming {self.__class__.__name__}...")
        
        self.tree = tree
        
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        func = FunctionTransformer.FunctionTransformer(self.alphabet, self.length)
        self.tree = func.visit(self.tree)
        
        return self.tree
    
    class FunctionTransformer(ast.NodeTransformer):
        
        def __init__(self, alphabet, length):
            self.alphabet = alphabet
            self.length = length
        
        def visit_FunctionDef(self, node: ast.FunctionDef):
            if node.name.startswith("__"): return node
            if len(node.args.args) == 0: return node
            
            args_name = Utils.randomize_name(self.alphabet, self.length)
            node.args.vararg = ast.arg(arg=args_name)
            
            i = 0
            for arg in node.args.args:
                node.body.insert(0, 
                    ast.Assign(
                        targets=[
                            ast.Name(id=arg.arg)],
                        value=ast.Subscript(
                            value=ast.Name(id=args_name),
                            slice=ast.Constant(value=i)
                        ),
                        lineno = None
                    )
                )
                i += 1
            
            for i in range(random.randint(0, 6)):
                arg_name = Utils.randomize_name(self.alphabet, self.length)
                
                j = i
                if i > len(node.args.args) - 1:
                    j = random.randint(0, len(node.args.args) - 1)
                
                node.body.insert(0, 
                    ast.Assign(
                        targets=[
                            ast.Name(id=arg_name)],
                        value=ast.Subscript(
                            value=ast.Name(id=args_name),
                            slice=ast.Constant(value=j)
                        ),
                        lineno = None
                    )
                )
            
            node.args.args = []
            
            mutate_name = Utils.randomize_name(self.alphabet, self.length)
            stop_code = random.randint(1000000, 1000000000000)
            stop_code_key = random.randint(1000000, 1000000000000)
            
            node.body = [ast.Assign(
                targets=[
                    ast.Name(id=mutate_name)],
                value=ast.Constant(value=stop_code ^ stop_code_key),
                lineno=None),
            ast.While(
                test=ast.Compare(
                    left=ast.Name(id=mutate_name),
                    ops=[
                        ast.NotEq()],
                    comparators=[
                        ast.Constant(value=stop_code)]),
                body=[
                    ast.Expr(
                        value=ast.AugAssign(
                            target=ast.Name(id=mutate_name),
                            op=ast.BitXor(),
                            value=ast.Constant(value=stop_code_key)))] + node.body,
                orelse=[])]
            
            return node