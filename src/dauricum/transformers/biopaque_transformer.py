
import ast, random
from dauricum.transformers.base import Transformer
from dauricum.tools.utils import Utils
from dauricum.tools.logger import Logger

class BiOpaqueUtils:
    
    def generate_expression(value):
        pass

class BiOpaqueTransformer(Transformer):
        
    def proceed(self, tree: ast.Module):
        Logger.logger.name = __class__.__name__
        Logger.logger.info(f"transforming {self.__class__.__name__}...")
        
        self.tree = tree
        
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        biopaque = BiOpaqueTransformer.BiOpaqueTransformer()
        self.tree = biopaque.visit(self.tree)
        
        return self.tree
    
    class BiOpaqueTransformer(ast.NodeTransformer):
        def visit_Assign(self, node: ast.Assign):
            
            
            return node