
import ast, random
from dauricum.transformers.base import Transformer
from dauricum.tools.utils import Utils
from dauricum.tools.logger import Logger

class ExceptionJumpUtils:
    alphabet = "abcde1234"
    length = 16
    
    def generate_junk(ex_name: str, max: int):
        cases = []
        
        line = max + 1
        for i in range (random.randint(0, 3)):
            case_name = Utils.randomize_name(ExceptionJumpUtils.alphabet, ExceptionJumpUtils.length)
            
            cases.append(
                ast.If(
                    test=ast.Compare(
                        left=ast.Subscript(
                            value=ast.Attribute(
                                value=ast.Name(id=ex_name),
                                attr='args'),
                            slice=ast.Constant(value=0)),
                        ops=[
                            ast.Eq()],
                        comparators=[
                            ast.Constant(value=line)]),
                    body=[
                        ast.Assign(
                            targets=[
                                ast.Name(id=case_name)
                            ],
                            value=ast.Constant(value=random.randint(0xFFFFF, 0xFFFFFFFFFFFF)),
                            lineno=None
                        )
                    ],
                    orelse=[]
                )
            )
            line += 1
        
        return cases
    
    def generate_blockV(body):
        old_body = body
        
        body = []
        var_name = Utils.randomize_name(ExceptionJumpUtils.alphabet, ExceptionJumpUtils.length)
        ex_name = Utils.randomize_name(ExceptionJumpUtils.alphabet, ExceptionJumpUtils.length)
        
        body.append(ast.Assign(
                targets=[
                    ast.Name(id=var_name)
                ],
                value=ast.Constant(value=0),
                lineno=None
            )
        )
        
        case = ast.While(
        test=ast.Compare(
            left=ast.Name(id=var_name),
            ops=[
                ast.NotEq()],
            comparators=[
                ast.Constant(value=len(old_body) + 1)]),
        body=[
            ast.AugAssign(
                target=ast.Name(id=var_name),
                op=ast.Add(),
                value=ast.Constant(value=1)),
            ast.Try(
                body=[
                    ast.Raise(
                        exc=ast.Call(
                            func=ast.Name(id='ValueError'),
                            args=[
                                ast.Name(id=var_name)],
                            keywords=[]))],
                handlers=[
                    ast.ExceptHandler(
                        type=ast.Name(id='ValueError'),
                        name=ex_name,
                        body=[])],
                orelse=[],
                finalbody=[])],
        orelse=[])
        
        line = 1
        for body_node in old_body:
            case.body[1].handlers[0].body.append(
                ast.If(
                    test=ast.Compare(
                        left=ast.Subscript(
                            value=ast.Attribute(
                                value=ast.Name(id=ex_name),
                                attr='args'),
                            slice=ast.Constant(value=0)),
                        ops=[
                            ast.Eq()],
                        comparators=[
                            ast.Constant(value=line)]),
                    body=[
                        body_node
                    ],
                    orelse=[]))
            line += 1
        
        case.body[1].handlers[0].body.append(ExceptionJumpUtils.generate_junk(ex_name, len(old_body) + 1))
        random.shuffle(case.body[1].handlers[0].body)
        
        body.append(case)
        
        return body
    
    def generate_block(node):
        old_body = node.body
        
        node.body = []
        var_name = Utils.randomize_name(ExceptionJumpUtils.alphabet, ExceptionJumpUtils.length)
        ex_name = Utils.randomize_name(ExceptionJumpUtils.alphabet, ExceptionJumpUtils.length)
        
        node.body.append(ast.Assign(
                targets=[
                    ast.Name(id=var_name)
                ],
                value=ast.Constant(value=0),
                lineno=None
            )
        )
        
        case = ast.While(
        test=ast.Compare(
            left=ast.Name(id=var_name),
            ops=[
                ast.NotEq()],
            comparators=[
                ast.Constant(value=len(old_body) + 1)]),
        body=[
            ast.AugAssign(
                target=ast.Name(id=var_name),
                op=ast.Add(),
                value=ast.Constant(value=1)),
            ast.Try(
                body=[
                    ast.Raise(
                        exc=ast.Call(
                            func=ast.Name(id='ValueError'),
                            args=[
                                ast.Name(id=var_name)],
                            keywords=[]))],
                handlers=[
                    ast.ExceptHandler(
                        type=ast.Name(id='ValueError'),
                        name=ex_name,
                        body=[])],
                orelse=[],
                finalbody=[])],
        orelse=[])
        
        globals_list = []
        
        line = 1
        for body_node in old_body:
            if isinstance(body_node, ast.Global):
                globals_list.append(body_node)
                continue
            
            case.body[1].handlers[0].body.append(
                ast.If(
                    test=ast.Compare(
                        left=ast.Subscript(
                            value=ast.Attribute(
                                value=ast.Name(id=ex_name),
                                attr='args'),
                            slice=ast.Constant(value=0)),
                        ops=[
                            ast.Eq()],
                        comparators=[
                            ast.Constant(value=line)]),
                    body=[
                        body_node
                    ],
                    orelse=[]))
            line += 1
        
        case.body[1].handlers[0].body.append(ExceptionJumpUtils.generate_junk(ex_name, len(old_body) + 1))
        random.shuffle(case.body[1].handlers[0].body)
        
        node.body.append(case)
        
        for global_obj in globals_list:
            node.body.insert(0, global_obj)
        
        return node

class ExceptionJumpTransformer(Transformer):
    
    def __init__(self, alphabet: str, length: int):
        ExceptionJumpUtils.alphabet = alphabet
        ExceptionJumpUtils.length = length
    
    def proceed(self, tree: ast.Module):
        Logger.logger.name = __class__.__name__
        Logger.logger.info(f"transforming {self.__class__.__name__}...")
        
        self.tree = tree
        
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        renamer = ExceptionJumpTransformer.ExceptionJumpTransformer()
        self.tree = renamer.visit(self.tree)
        
        return self.tree
    
    class ExceptionJumpTransformer(ast.NodeTransformer):
        
        def visit_FunctionDef(self, node: ast.FunctionDef):
            node = ExceptionJumpUtils.generate_block(node)
            
            return node
        def visit_If(self, node: ast.If):
            node = ExceptionJumpUtils.generate_block(node)
            
            return node
        def visit_Assign(self, node: ast.Assign):
            node = ExceptionJumpUtils.generate_blockV([node])
            
            return node