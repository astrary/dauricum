
import ast, random, math
from dauricum.transformers.base import Transformer
from dauricum.tools.utils import Utils
from dauricum.tools.logger import Logger

class StringUtils:
    alphabet = "abcde01234"
    length = 16
    
    def encrypt_string(key1, key2, key3, string):
        keys = []
        
        for i in range(string.__len__()):
            key1 = key1 % 256 
            key2 = key2 % 25
            key3 = key3 % 9999
            
            keys.append(ord(string[i]) ^ (key1, key2, key3)[i % 3])
            
            key1 = key2 << key1 % 16
            key2 = math.ceil(key2 / (key1 + 1)) ^ key3
            key3 = (key1 - key2) ^ key3
            key1, key2, key3 = key2, key3, key1
        
        return keys
    
    def obfuscate(string: str):
        key1 = random.randint(1, 256)
        key2 = random.randint(1, 25)
        key3 = random.randint(1, 9999)
        key2 = (key2 % 2) + key2
        
        keys = StringUtils.encrypt_string(key1, key2, key3, string)
        keys_parsed = ast.parse(str(keys)).body[0].value
        
        (n1, n2, n3, n4, n5, n6) = [Utils.randomize_name(StringUtils.alphabet, StringUtils.length) for i in range(6)]
        
        # https://egirl.rip/e/stFsMTU9qp.gif?key=RYg5m5fRwxnwek
        block = ast.Call(func=ast.Lambda(args=ast.arguments(posonlyargs=[],args=[ast.arg(arg=n1),ast.arg(arg=n2),ast.arg(arg=n3),ast.arg(arg=n4),ast.arg(arg=n5),ast.arg(arg=n6)],kwonlyargs=[],kw_defaults=[],defaults=[]),body=ast.Subscript(value=ast.Subscript(value=ast.Subscript(value=ast.Tuple(elts=[ast.ListComp(elt=ast.Tuple(elts=[ast.ListComp(elt=ast.Call(func=ast.Attribute(value=ast.Name(id=n1),attr='__setitem__'),args=[ast.Name(id='j'),ast.BinOp(left=ast.Subscript(value=ast.Name(id=n1),slice=ast.Name(id='j')),op=ast.Mod(),right=ast.Subscript(value=ast.Subscript(value=ast.List(elts=[ast.Constant(value=9999),ast.Constant(value=25),ast.Constant(value=256)]),slice=ast.Slice(step=ast.UnaryOp(op=ast.USub(),operand=ast.Name(id=n4)))),slice=ast.Name(id='j')))],keywords=[]),generators=[ast.comprehension(target=ast.Name(id='j'),iter=ast.Call(func=ast.Name(id='range'),args=[ast.BinOp(left=ast.Name(id=n6),op=ast.Add(),right=ast.Name(id=n4))],keywords=[]),ifs=[],is_async=0)]),ast.Call(func=ast.Call(func=ast.Name(id='getattr'),args=[ast.Name(id=n3),ast.Constant(value='append')],keywords=[]),args=[ast.BinOp(left=ast.Subscript(value=ast.Name(id=n2),slice=ast.Name(id='i')),op=ast.BitXor(),right=ast.Subscript(value=ast.Tuple(elts=[ast.Subscript(value=ast.Name(id=n1),slice=ast.Constant(value=0)),ast.Subscript(value=ast.Name(id=n1),slice=ast.Constant(value=1)),ast.Subscript(value=ast.Name(id=n1),slice=ast.Constant(value=2))]),slice=ast.BinOp(left=ast.Name(id='i'),op=ast.Mod(),right=ast.BinOp(left=ast.Name(id=n6),op=ast.Add(),right=ast.Name(id=n4)))))],keywords=[]),ast.Call(func=ast.Attribute(value=ast.Name(id=n1),attr='__setitem__'),args=[ast.Name(id=n5),ast.BinOp(left=ast.Subscript(value=ast.Name(id=n1),slice=ast.Name(id=n4)),op=ast.LShift(),right=ast.BinOp(left=ast.Subscript(value=ast.Name(id=n1),slice=ast.Constant(value=0)),op=ast.Mod(),right=ast.BinOp(left=ast.Name(id=n6),op=ast.Mult(),right=ast.Constant(value=8))))],keywords=[]),ast.Call(func=ast.Attribute(value=ast.Name(id=n1),attr='__setitem__'),args=[ast.Name(id=n4),ast.BinOp(left=ast.Call(func=ast.Call(func=ast.Name(id='getattr'),args=[ast.Call(func=ast.Name(id='__import__'),args=[ast.Constant(value='math')],keywords=[]),ast.Constant(value='ceil')],keywords=[]),args=[ast.BinOp(left=ast.Subscript(value=ast.Name(id=n1),slice=ast.Name(id=n4)),op=ast.Div(),right=ast.BinOp(left=ast.Subscript(value=ast.Name(id=n1),slice=ast.Name(id=n5)),op=ast.Add(),right=ast.Name(id=n4)))],keywords=[]),op=ast.BitXor(),right=ast.Subscript(value=ast.Name(id=n1),slice=ast.Name(id=n6)))],keywords=[]),ast.Call(func=ast.Attribute(value=ast.Name(id=n1),attr='__setitem__'),args=[ast.Name(id=n6),ast.BinOp(left=ast.BinOp(left=ast.Subscript(value=ast.Name(id=n1),slice=ast.Name(id=n5)),op=ast.Sub(),right=ast.Subscript(value=ast.Name(id=n1),slice=ast.Name(id=n4))),op=ast.BitXor(),right=ast.Subscript(value=ast.Name(id=n1),slice=ast.Name(id=n6)))],keywords=[]),ast.ListComp(elt=ast.Tuple(elts=[ast.List(elts=[ast.Call(func=ast.Attribute(value=ast.Name(id=n1),attr='insert'),args=[ast.Name(id=n5),ast.Subscript(value=ast.Name(id=n1),slice=ast.Name(id=n6))],keywords=[])]),ast.List(elts=[ast.Call(func=ast.Attribute(value=ast.Name(id=n1),attr='pop'),args=[],keywords=[])])]),generators=[ast.comprehension(target=ast.Name(id='j'),iter=ast.Call(func=ast.Name(id='range'),args=[ast.Name(id=n6)],keywords=[]),ifs=[],is_async=0)])]),generators=[ast.comprehension(target=ast.Name(id='i'),iter=ast.Call(func=ast.Name(id='range'),args=[ast.Call(func=ast.Call(func=ast.Name(id='getattr'),args=[ast.Name(id=n2),ast.Constant(value='__len__')],keywords=[]),args=[],keywords=[])],keywords=[]),ifs=[],is_async=0)]),ast.Call(func=ast.Attribute(value=ast.Constant(value=''),attr='join'),args=[ast.ListComp(elt=ast.Call(func=ast.Name(id='chr'),args=[ast.Name(id='a')],keywords=[]),generators=[ast.comprehension(target=ast.Name(id='a'),iter=ast.Name(id=n3),ifs=[],is_async=0)])],keywords=[])]),slice=ast.Slice(step=ast.UnaryOp(op=ast.USub(),operand=ast.Constant(value=1)))),slice=ast.Slice(upper=ast.Constant(value=1))),slice=ast.Constant(value=0))),args=[ast.Starred(value=ast.Tuple(elts=[ast.Call(func=ast.Lambda(args=ast.arguments(posonlyargs=[],args=[],kwonlyargs=[],kw_defaults=[],defaults=[]),body=ast.Subscript(value=ast.List(elts=[ast.Constant(value=key1),ast.Constant(value=key2),ast.Constant(value=key3)][::-1]),slice=ast.Slice(step=ast.UnaryOp(op=ast.USub(),operand=ast.Constant(value=1))))),args=[],keywords=[]),ast.Call(func=ast.Lambda(args=ast.arguments(posonlyargs=[],args=[],kwonlyargs=[],kw_defaults=[],defaults=[]),body=keys_parsed),args=[],keywords=[]),ast.Call(func=ast.Lambda(args=ast.arguments(posonlyargs=[],args=[],kwonlyargs=[],kw_defaults=[],defaults=[]),body=ast.BinOp(left=ast.Subscript(value=ast.List(elts=[ast.Constant(value=0),ast.Constant(value=1),ast.Constant(value=2),ast.Constant(value=3),ast.Constant(value=4),ast.Constant(value=5),ast.Constant(value=6)]),slice=ast.Slice(step=ast.UnaryOp(op=ast.USub(),operand=ast.Constant(value=1)))),op=ast.Mult(),right=ast.UnaryOp(op=ast.USub(),operand=ast.Constant(value=2)))),args=[],keywords=[]),ast.Starred(value=ast.Tuple(elts=[ast.Call(func=ast.Lambda(args=ast.arguments(posonlyargs=[],args=[],kwonlyargs=[],kw_defaults=[],defaults=[]),body=ast.Constant(value=1)),args=[],keywords=[]),ast.Call(func=ast.Lambda(args=ast.arguments(posonlyargs=[],args=[],kwonlyargs=[],kw_defaults=[],defaults=[]),body=ast.Constant(value=0)),args=[],keywords=[]),ast.Call(func=ast.Lambda(args=ast.arguments(posonlyargs=[],args=[],kwonlyargs=[],kw_defaults=[],defaults=[]),body=ast.Constant(value=2)),args=[],keywords=[])]))]))],keywords=[])
        
        return block

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
            
            return StringUtils.obfuscate(node.value)