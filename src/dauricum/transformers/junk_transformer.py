
import ast, random
from dauricum.transformers.base import Transformer
from dauricum.tools.utils import Utils
from dauricum.tools.logger import Logger

class JunkTransformer(Transformer):
    
    def proceed(self, tree: ast.Module):
        Logger.logger.name = __class__.__name__
        Logger.logger.info(f"transforming {self.__class__.__name__}...")
        
        self.tree = tree
        
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        renamer = JunkTransformer.JunkTransformer()
        self.tree = renamer.visit(self.tree)
        
        return self.tree
    
    class JunkTransformer(ast.NodeTransformer):
        def visit_If(self, node: ast.If):
            node.body.append(
                ast.If(
                    test=ast.Compare(
                        left=ast.Name(id='_', ctx=ast.Load()),
                        ops=[
                            ast.Eq()],
                        comparators=[
                            ast.Constant(value=1)]),
                    body=[],
                    orelse=[]
                )
            )
            
            return node