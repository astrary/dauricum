
import ast, random
from dauricum.transformers.base import Transformer
from dauricum.tools.utils import Utils
from dauricum.tools.logger import Logger

class FormatHelper:
    def convert_pinterpolation(string: str):
        splitted_string = string.split('%')
        if not string.startswith('%'): splitted_string.pop(0)
        
        fmt_list = ['d', 'i', 'o', 'u', 'x', 'X', 'e', 'E', 'f', 'F', 'g', 'G']
        op_list = ['#', '0', '-', '+', 'c', 'b', 'a', 's']
        
        ret_string = string
        
        for word in splitted_string:
            t_word = "%"
            
            for char in word:
                if char == ' ': break
                if not char in fmt_list: 
                    if char in op_list:
                        if len(t_word) > 1 and t_word[1] in fmt_list:
                            break
                    else:
                        break
                
                if char in fmt_list and len(t_word) > 1: break
                
                t_word += char
            ret_string = ret_string.replace(t_word, "{}")
        
        return ret_string

class FormatTransformer(Transformer):
    
    def proceed(self, tree: ast.Module):
        Logger.logger.name = __class__.__name__
        Logger.logger.info(f"transforming {self.__class__.__name__}...")
        
        self.tree = tree
        
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        formatter = FormatTransformer.FormatTransformer()
        self.tree = formatter.visit(self.tree)
        
        return self.tree
    
    class FormatTransformer(ast.NodeTransformer):
        
        def visit_JoinedStr(self, node: ast.JoinedStr):
            fmt_string = ""
            fmt_keywords = []
            
            for formatter in node.values:
                if isinstance(formatter, ast.Constant):
                    fmt_string += formatter.value
                elif isinstance(formatter, ast.FormattedValue):
                    fmt_name = Utils.randomize_name("abcde01234", 16)
                    
                    fmt_string += "{%s}" % (fmt_name)
                    fmt_keywords.append(ast.keyword(arg=fmt_name, value=formatter.value))
                else:
                    raise NotImplementedError("formatter not implemented %s" % (formatter))
            
            node = ast.Call(
                func=ast.Attribute(
                    value=ast.Constant(value=fmt_string),
                    attr='format'
                ),
                args=[],
                keywords=fmt_keywords
            )
            
            return node
        
        def visit_BinOp(self, node: ast.BinOp):
            if not isinstance(node.left, ast.Constant): return node
            if not isinstance(node.left.value, str): return node
            if not isinstance(node.op, ast.Mod): return node
            
            fmt_string = FormatHelper.convert_pinterpolation(node.left.value)
            
            node = ast.Call(
                func=ast.Attribute(
                    value=ast.Constant(value=fmt_string),
                    attr='format'
                ),
                args=node.right.elts,
                keywords=[]
            )
            
            return node