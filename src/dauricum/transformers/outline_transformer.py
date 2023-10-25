
import ast
from dauricum.transformers.base import Transformer
from dauricum.tools.utils import Utils
from dauricum.tools.logger import Logger

class OutlineTransformer(Transformer):
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
        
        outline = OutlineTransformer.OutlineTransformer(self.alphabet, self.length)
        self.tree = outline.visit(self.tree)
        
        return self.tree
    
    class OutlineTransformer(ast.NodeTransformer):
        def __init__(self, alphabet: str, length: int):
            self.alphabet = alphabet
            self.length = length
            
        def visit_Expr(self, node: ast.Expr):
            if not isinstance(node.value, ast.Call) or node.value.keywords != []:
                return node
            node_value = node.value
            
            if isinstance(node.value.func, ast.Attribute):
                if isinstance(node.value.func.value, ast.Call) and node.value.func.value.func.id == "super":
                    return node
            
            name = ast.Name(id=Utils.randomize_name(self.alphabet, self.length))
            
            node.value = ast.Call(
                func=name,
                args=node_value.args,
                keywords=node_value.keywords
            )
            
            argz = [ast.arg(arg=Utils.randomize_name(self.alphabet, self.length)) for i in range(len(node_value.args))]
                
            node_value.args = argz
            
            outline_body = ast.Assign(
                targets=[
                    name
                ],
                value=ast.Lambda(
                    args=ast.arguments(
                        posonlyargs=[],
                        args=node_value.args,
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[]
                    ),
                    body=node_value
                ),
                lineno=None
            )
            
            return [outline_body, node]
        
        def visit_Assign(self, node: ast.Assign):
            node_value = node.value
            
            if isinstance(node_value, ast.Call):
                if (node_value.keywords != []): return node
                name = node.value.func
                
                if isinstance(name, ast.Name):
                    name = name.id
                elif isinstance(name, ast.Attribute):
                    name = name.value
                else:
                    return node
                
                name = ast.Name(id=Utils.randomize_name(self.alphabet, self.length))
                
                node.value = ast.Call(
                    func=name,
                    args=node_value.args,
                    keywords=node_value.keywords
                )
                
                argz = [ast.arg(arg=Utils.randomize_name(self.alphabet, self.length)) for i in range(len(node_value.args))]
                
                node_value.args = argz
                
                outline_body = ast.Assign(
                    targets=[
                        name
                    ],
                    value=ast.Lambda(
                        args=ast.arguments(
                            posonlyargs=[],
                            args=node_value.args,
                            kwonlyargs=[],
                            kw_defaults=[],
                            defaults=[]
                        ),
                        body=node_value
                    ),
                    lineno=None
                )
                
                return [outline_body, node]
            
            return node