
import ast
from dauricum.transformers.base import Transformer
from dauricum.tools.logger import Logger

class ImportTransformer(Transformer):
    
    def proceed(self, tree: ast.Module):
        Logger.logger.name = __class__.__name__
        Logger.logger.info(f"transforming {self.__class__.__name__}...")
        
        self.tree = tree
        
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        importer = ImportTransformer.ImportTransformer()
        self.tree = importer.visit(self.tree)
        
        return self.tree
    
    class ImportTransformer(ast.NodeTransformer):
        
        def visit_ImportFrom(self, node: ast.ImportFrom):
            ret = []
            module_name = node.module
            
            for alias in node.names:
                name = alias.name
                asname = alias.asname
                
                if asname == None: asname = name
                
                if name == '*': 
                    return node
                
                ret.append(ast.Assign(
                    targets=[
                        ast.Name(id=name)],
                        value=ast.Call(
                            func=ast.Name(id='getattr'),
                            args=[
                                ast.Call(
                                    func=ast.Name(id='__import__'),
                                    args=[],
                                    keywords=[
                                        ast.keyword(
                                            arg='name',
                                            value=ast.Constant(s=module_name)),
                                        ast.keyword(
                                            arg='fromlist',
                                            value=ast.Constant(s=name))]),
                                ast.Constant(s=name)],
                            keywords=[]), lineno=None))
            
            return ret
        
        def visit_Import(self, node: ast.Import):
            ret = []
            
            for alias in node.names:
                name = alias.name
                asname = alias.asname
                
                if asname == None: asname = name
                
                ret.append(ast.Assign(
                    targets=[
                        ast.Name(id=asname)
                    ],
                    value=ast.Call(
                        func=ast.Name(id='__import__'),
                        args=[
                            ast.Constant(value=name)],
                        keywords=[ast.keyword(
                            arg='fromlist',
                            value=ast.List(
                                elts=[
                                    ast.Constant(value=None)
                                ]
                            )
                        )]
                    ),
                    lineno=None
                ))
            
            return ret