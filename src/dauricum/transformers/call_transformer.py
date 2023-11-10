
import ast, builtins, random
from dauricum.transformers.base import Transformer
from dauricum.tools.utils import Utils
from dauricum.tools.logger import Logger

class CallUtils:
    
    def get_object_for_letter(letter):
        objs = dir(builtins)
        random.shuffle(objs)
        
        for obj in objs:
            if letter in obj and hasattr(getattr(builtins, obj), '__name__') and getattr(builtins, obj).__name__ == obj and ('exception' in obj.lower() or 'error' in obj.lower() or '__' in obj.lower()):
                return [obj, obj.find(letter)]
            
        Logger.logger.debug(f"for letter '{letter}' not found any candidate!")
        return None
    
    def generate_builtin_attr_block(node: ast.Call):
        name = node.func.id
        
        block = ast.Call(
            func=ast.Call(
                func=ast.Name(id='getattr'),
                args=[
                    ast.Name(id='__builtins__'),
                    ast.Call(
                        func=ast.Attribute(
                            value=ast.Constant(value=''),
                            attr='join'),
                        args=[
                            ast.List(
                                elts=[])],
                        keywords=[])],
                keywords=[]
            ),
            args=node.args,
            keywords=node.keywords
        )
        
        for letter in name:
            obj = CallUtils.get_object_for_letter(letter)
            
            block.func.args[1].args[0].elts.append(
                ast.Subscript(
                    value=ast.Attribute(
                        value=ast.Name(id=obj[0]),
                        attr='__name__'),
                    slice=ast.Constant(value=obj[1])
                )
            )
        
        return block
    
    def generate_attribute_attr_block(node: ast.Call):
        name = node.func.attr
        value = node.func.value
        
        if not isinstance(value, ast.Name):
            return node
        
        block = ast.Call(
            func=ast.Call(
                func=ast.Name(id='getattr'),
                args=[
                    ast.Name(id=value.id),
                    ast.Call(
                        func=ast.Attribute(
                            value=ast.Constant(value=''),
                            attr='join'),
                        args=[
                            ast.List(
                                elts=[])],
                        keywords=[])],
                keywords=[]
            ),
            args=node.args,
            keywords=node.keywords
        )
        
        for letter in name:
            obj = CallUtils.get_object_for_letter(letter)
            
            block.func.args[1].args[0].elts.append(
                ast.Subscript(
                    value=ast.Attribute(
                        value=ast.Name(id=obj[0]),
                        attr='__name__'),
                    slice=ast.Constant(value=obj[1])
                )
            )
        
        return block

class CallTransformer(Transformer):
        
    def proceed(self, tree: ast.Module):
        Logger.logger.name = __class__.__name__
        Logger.logger.info(f"transforming {self.__class__.__name__}...")
        
        self.tree = tree
        
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        call = CallTransformer.CallTransformer()
        self.tree = call.visit(self.tree)
        
        return self.tree
    
    class CallTransformer(ast.NodeTransformer):
        def visit_Call(self, node: ast.Call):
            
            if (isinstance(node.func, ast.Name)):
                is_builtin = str(node.func.id) in dir(builtins)
                
                if is_builtin:
                    return CallUtils.generate_builtin_attr_block(node)
            # elif (isinstance(node.func, ast.Attribute)): # Bugged
            #     return CallUtils.generate_attribute_attr_block(node)
            
            return node