
import ast, random
from dauricum.transformers.base import Transformer
from dauricum.tools.utils import Utils
from dauricum.tools.logger import Logger

class StringUtils:
    alphabet = "abcde01234"
    length = 16
    
    def generate_block(string):
        keys = [random.randint(0, 127) for i in range(len(string) + random.randint(16, 32))]
        obfuscated_string = [ ord(string[i]) ^ keys[i] for i in range(len(string)) ]
        key_var_name = Utils.randomize_name(StringUtils.alphabet, StringUtils.length)
        
        sample = ast.Call(
            func=ast.Lambda(
                args=ast.arguments(
                    posonlyargs=[],
                    args=[
                        ast.arg(arg=key_var_name)],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[]),
                body=ast.Call(
                    func=ast.Attribute(
                        value=ast.Constant(value=''),
                        attr='join'),
                    args=[
                        ast.List(
                            elts=[
                                ])],
                    keywords=[])),
            args=[
                ast.Constant(value=''.join([chr(key) for key in keys]))],
            keywords=[])
        
        elts = []
        for i in range(len(obfuscated_string)):
            elts.append(ast.Call(
                func=ast.Lambda(
                    args=ast.arguments(
                        posonlyargs=[],
                        args=[
                            ast.arg(arg=key_var_name)],
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[]),
                    body=ast.Call(
                        func=ast.Name(id='chr'),
                        args=[ast.BinOp(
                            left=ast.Constant(value=obfuscated_string[i]),
                            op=ast.BitXor(),
                            right=ast.Call(
                                func=ast.Name(id='ord'),
                                args=[
                                    ast.Name(id=key_var_name)],
                                keywords=[])
                        )],
                        keywords=[])),
                args=[
                    ast.Subscript(
                        value=ast.Name(id=key_var_name),
                        slice=ast.Constant(value=i))],
                keywords=[]
            ))
        sample.func.body.args[0].elts = elts
        return sample
        

class StringTransformer(Transformer):
    
    def __init__(self, alphabet: str, length: int):
        StringUtils.alphabet = alphabet
        StringUtils.length = length
        
    def proceed(self, tree: ast.Module):
        Logger.logger.name = __class__.__name__
        Logger.logger.info(f"transforming {self.__class__.__name__}...")
        
        self.tree = tree
        
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        string = StringTransformer.StringTransformer()
        self.tree = string.visit(self.tree)
        
        return self.tree
    
    class StringTransformer(ast.NodeTransformer):
        def visit_Constant(self, node: ast.Constant):
            if (not isinstance(node.value, str)): return node
            if (isinstance(node.parent, ast.JoinedStr)): return node
            
            return StringUtils.generate_block(node.value)