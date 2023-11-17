
import ast, random, copy, gc
from dauricum.transformers.base import Transformer
from dauricum.tools.utils import Utils
from dauricum.tools.logger import Logger

class BiOpaqueUtils:
    possible_args = []
    possible_functions = []
    alphabet = "abcde01234"
    length = 16
    safe_mode = False
    
    def get_possible_functions(tree: ast.Module):
        if BiOpaqueUtils.possible_functions != []: return BiOpaqueUtils.possible_functions
        
        possible_functions = [ast.Name(id=func_id) for func_id in dir(__builtins__) if not func_id.startswith("_")]
        
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.FunctionDef):
                    if isinstance(child.parent, ast.ClassDef):
                        possible_functions.append(ast.Attribute(value=ast.Name(id=child.parent.name), attr=child.name))
                    else:
                        possible_functions.append(ast.Name(id=child.name))
        
        BiOpaqueUtils.possible_functions = possible_functions
        
        return BiOpaqueUtils.possible_functions
    
    def get_possible_args(tree: ast.Module):
        if BiOpaqueUtils.possible_args != []: return BiOpaqueUtils.possible_args
        
        possible_args = []
        
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.Call):
                    for arg in child.args:
                        possible_args.append(arg)
        
        BiOpaqueUtils.possible_args = possible_args
        
        return BiOpaqueUtils.possible_args
        
    def get_random_function(tree: ast.Module):
        possible_functions = BiOpaqueUtils.get_possible_functions(tree)
        
        return random.choice(possible_functions)
    
    def get_random_args(tree: ast.Module):
        possible_args = BiOpaqueUtils.get_possible_args(tree)
        
        return [random.choice(possible_args) for i in range(random.randint(0, 2))]
    
    def generate_bogus_body(tree, node):
        bogus = type(node).__new__(type(node))
        bogus.__dict__.update(node.__dict__)
        
        for name, field in ast.iter_fields(bogus):
            if isinstance(field, ast.Call):
                new_call = type(field).__new__(type(field))
                new_call.__dict__.update(field.__dict__)
                
                if isinstance(new_call.func, ast.Name) or isinstance(new_call.func, ast.Attribute):
                    new_call.func = BiOpaqueUtils.get_random_function(tree)
                    new_call.args = BiOpaqueUtils.get_random_args(tree)
                
                setattr(bogus, name, new_call)
            if isinstance(bogus, ast.Assign) and name == 'value':
                new_value = random.choice(BiOpaqueUtils.get_possible_args(tree))
                if isinstance(bogus.value, ast.List) or isinstance(bogus.value, ast.Dict):
                    new_value = ast.List(elts=[random.choice(BiOpaqueUtils.get_possible_args(tree)) for ignored in range(random.randint(2, 6))])
                
                setattr(bogus, name, new_value)
            if isinstance(bogus, ast.AugAssign) and name == 'value':
                new_value = random.choice(BiOpaqueUtils.get_possible_args(tree))
                if isinstance(bogus.value, ast.List) or isinstance(bogus.value, ast.Dict):
                    new_value = ast.List(elts=[random.choice(BiOpaqueUtils.get_possible_args(tree)) for ignored in range(random.randint(2, 6))])
                
                setattr(bogus, name, new_value)
                setattr(bogus, 'op', random.choice([ast.Add(), ast.Sub(), ast.Div(), ast.Mult(), ast.BitXor(), *([node.op] * 3)] ))
        
        return bogus
    
    def generate_roadline(goal: int):
        num = random.randint(1, 100)
        current_num = num
        roadline = []

        while current_num != goal:
            if current_num > goal:
                val = random.randint(1, num + 1)
                current_num -= val
                roadline.append([ast.Sub(), val])
            elif current_num < goal:
                val = random.randint(1, num + 1)
                current_num += val
                roadline.append([ast.Add(), val])
        return (num, roadline)
    
    def obscure_bool(value: bool, arg_name: str):
        roadline = BiOpaqueUtils.generate_roadline(value)
        
        while len(roadline[1]) > 6:
            roadline = BiOpaqueUtils.generate_roadline(value)
        
        original_number = roadline[0]
        roadline = roadline[1]
        
        binop_name = Utils.randomize_name(BiOpaqueUtils.alphabet, BiOpaqueUtils.length)
        binop = ast.Name(id=binop_name)
        
        for action in roadline:
            key = random.randint(1, 6996)
            xored_binop = ast.BinOp(left=ast.Constant(action[1] ^ key), op=ast.BitXor(), right=ast.Constant(value=key))
            
            binop = ast.BinOp(
                left=binop,
                op=action[0],
                right=ast.Call(
                    func=ast.Lambda(
                        args=ast.arguments(
                            posonlyargs=[],
                            args=[],
                            kwonlyargs=[],
                            kw_defaults=[],
                            defaults=[]),
                        body=xored_binop
                    ),
                    args=[],
                    keywords=[]
                )
            )
        
        if BiOpaqueUtils.safe_mode:
            return (ast.Call(
                func=ast.Lambda(
                    args=ast.arguments(
                        posonlyargs=[],
                        args=[ast.arg(arg=binop_name)],
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[]),
                    body=binop
                ),
                args=[ast.Constant(value=original_number)],
                keywords=[]
            ), None)
        
        return (ast.Call(
            func=ast.Lambda(
                args=ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg(arg=binop_name)],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[]),
                body=binop
            ),
            args=[ast.Name(id=arg_name)],
            keywords=[]
        ), original_number)
    
    def generate_opaquepredicate(tree, node, arg_name: str):
        test = BiOpaqueUtils.obscure_bool(True, arg_name)
        
        ret_node = ast.If(
            test=test[0],
            body=[
                node
            ],
            orelse=[
                BiOpaqueUtils.generate_bogus_body(tree, node)
            ]
        )
        
        if Utils.get_chance() > 50:
            test = BiOpaqueUtils.obscure_bool(False, arg_name)
            
            ret_node.body, ret_node.orelse = ret_node.orelse, ret_node.body
            ret_node.test = test[0]
        
        return (ret_node, test[1])
    
    def fix_calls(tree, func_name: str, arg_name: str, value: int):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Lambda):
                        continue
                    elif isinstance(child.func, ast.Name):
                        if child.func.id == func_name:
                            child.args.append(ast.Constant(value=value))
                    elif isinstance(child.func, ast.Attribute):
                        if child.func.attr == func_name:
                            child.args.append(ast.Constant(value=value))

class BiOpaqueTransformer(Transformer):
    
    def __init__(self, alphabet: str, length: int, safe_mode: bool):
        BiOpaqueUtils.alphabet = alphabet
        BiOpaqueUtils.length = length
        BiOpaqueUtils.safe_mode = safe_mode
        
    def proceed(self, tree: ast.Module):
        Logger.logger.name = __class__.__name__
        Logger.logger.info(f"transforming {self.__class__.__name__}...")
        
        self.tree = tree
        
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        biopaque = BiOpaqueTransformer.BiOpaqueTransformer(self.tree)
        self.tree = biopaque.visit(self.tree)
        self.tree = ast.parse(ast.unparse(tree))
        
        return self.tree
    
    class BiOpaqueTransformer(ast.NodeTransformer):
        def __init__(self, tree: ast.Module):
            self.tree = tree
        
        def visit_FunctionDef(self, node: ast.FunctionDef):
            if isinstance(node, list): return node
            if node.args.vararg != None or node.args.kwarg != None: return node
            if node.name.startswith("__"): return node
            Logger.logger.debug("proceeding biopaque function: " + node.name)
            
            body = node.body
            body_length = len(body)
            bad_list = [ast.Global, ast.If, ast.For, ast.Return, ast.Pass, ast.Try, ast.ExceptHandler]
            
            chance = 75
            chance_step = int(50 / (body_length))
            
            if body_length == 1: return node
            
            for i in range(body_length):
                child = body[i]
                if isinstance(child, list): continue
                
                if chance <= 0 or chance >= 100: break
                
                if (Utils.get_chance() > chance and not type(child) in bad_list):
                    arg_name = Utils.randomize_name(BiOpaqueUtils.alphabet, BiOpaqueUtils.length)
                    predicate = BiOpaqueUtils.generate_opaquepredicate(self.tree, child, arg_name)
                    
                    if not BiOpaqueUtils.safe_mode:
                        node.args.args.append(ast.arg(arg=arg_name))
                        BiOpaqueUtils.fix_calls(self.tree, node.name, arg_name, predicate[1])
                    
                    body[i] = predicate[0]
            
                    chance += chance_step
            
            return node