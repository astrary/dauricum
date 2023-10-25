
import ast, random
from dauricum.transformers.base import Transformer
from dauricum.tools.utils import Utils
from dauricum.tools.logger import Logger

class MutatorUtils:
    alphabet = "abcde01234"
    length = 16
    safe_mode = False
    
    def generate_stack_elts(real: int):
        elts = [ast.Constant(value=random.randint(0xFF * len(str(str(real))) * 100, 0xFFFFFF * len(str(str(real))) * 10)) for i in range(random.randint(0, 15))]
        elts.append(ast.Constant(value=real))
        random.shuffle(elts)
        
        index = -1
        for elt in elts:
            if (elt.value == real):
                index = elts.index(elt)
        
        return [elts, index]
    def proceed_int_assign(node: ast.Assign, ladder: int):
        old_value = node.value.value
        name = Utils.randomize_name(MutatorUtils.alphabet, MutatorUtils.length)
        
        keys = [~(random.randint(0xFF, 0xFFFFFFF)) for i in range(ladder)]
        obscured = old_value
        
        for key in keys:
            obscured = obscured ^ ~(key)
        
        elts = MutatorUtils.generate_stack_elts(obscured)
        stack = ast.Assign(
            targets=[
                ast.Name(id=name)],
            value=ast.List(
                elts=elts[0]
            ),
            lineno=None
        )
        
        key_index = random.randint(0xFF, 0xFFFFFFF)
        node.value.value = elts[1] ^ key_index
        
        body = []
        for key in keys:
            body.append(ast.Assign(
                targets=[
                    ast.Subscript(
                        value=ast.Name(id=name),
                        slice=ast.BinOp(
                            left=ast.Constant(value=key_index),
                            op=ast.BitXor(),
                            right=ast.Name(id=node.targets[0].id)))],
                value=ast.BinOp(
                    left=ast.Subscript(
                        value=ast.Name(id=name),
                        slice=ast.BinOp(
                            left=ast.Constant(value=key_index),
                            op=ast.BitXor(),
                            right=ast.Name(id=node.targets[0].id))),
                    op=ast.BitXor(),
                    right=ast.UnaryOp(
                        op=ast.Invert(),
                        operand=ast.Constant(value=key))),
                    lineno=None
                )
            )
        body.append(ast.Assign(
            targets=node.targets,
            value=ast.Subscript(
                value=ast.Name(id=name),
                slice=ast.BinOp(
                    left=ast.Constant(value=key_index),
                    op=ast.BitXor(),
                    right=ast.Name(id=node.targets[0].id))),
                    lineno=None
            )
        )
        
        return [node, stack, body]
    def proceed_int_list_assign(node: ast.Assign, ladder: int):
        for elt in node.value.elts:
            if (isinstance(elt, ast.Constant)):
                if (not isinstance(elt.value, int)):
                    return [node]
            else:
                return [node]
        
        old_elts = node.value.elts
        body = []
        name = node.targets[0].id
        
        for i in range(len(old_elts)):
            elt = old_elts[i]
            keys = [random.randint(-0xFFFFFFF, 0xFFFFFFF) for _ in range(ladder)]
            
            obscured_value = elt.value
            for key in keys:
                obscured_value ^= key
                body.append(
                    ast.AugAssign(
                        target=ast.Subscript(
                            value=ast.Name(id=name),
                            slice=ast.Constant(value=i)),
                        op=ast.BitXor(),
                        value=ast.Constant(value=key)
                    )
                )
            
            node.value.elts[i].value = obscured_value
        
        return [node, body]
    
    def proceed_float_list_assign(node: ast.Assign, ladder: int):
        for elt in node.value.elts:
            if (isinstance(elt, ast.Constant)):
                if (not isinstance(elt.value, float)):
                    return node
            else:
                return node
        
        old_elts = node.value.elts
        body = []
        name = node.targets[0].id
        
        for i in range(len(old_elts)):
            elt = old_elts[i]
            elt_point_len = len(str(elt.value).split('.')[1])
            
            keys = [random.uniform(-0xFFFFFFF, 0xFFFFFFF) for _ in range(ladder)]
            
            obscured_value = elt.value
            for key in keys:
                obscured_value += key
                body.append(
                    ast.AugAssign(
                        target=ast.Subscript(
                            value=ast.Name(id=name),
                            slice=ast.Constant(value=i)),
                        op=ast.Sub(),
                        value=ast.Constant(value=key)
                    )
                )
            body.append(
                ast.Assign(
                    targets=[
                        ast.Subscript(
                            value=ast.Name(id=name),
                            slice=ast.Constant(value=i))],
                    value=ast.Call(
                        func=ast.Name(id='round'),
                        args=[
                            ast.Subscript(
                                value=ast.Name(id=name),
                                slice=ast.Constant(value=i)
                            ),
                            ast.Constant(value=elt_point_len)],
                        keywords=[]),
                    lineno = None))
                
            node.value.elts[i].value = obscured_value
        
        return [node, body]
    
    def proceed_list_assign(node: ast.Assign, ladder: int):
        node = MutatorUtils.proceed_int_list_assign(node, ladder)
        
        if (len(node) > 1 or MutatorUtils.safe_mode == True):
            return node
        
        node = MutatorUtils.proceed_float_list_assign(node[0], ladder)
        
        return node
    
    def generate_binopt_int(value: int, keys):
        obscured_value = value
        
        for key in keys:
            obscured_value ^= key
            
        binopt = ast.BinOp(
            left = ast.Constant(value = obscured_value),
            op = ast.BitXor(),
            right = ast.Constant(value = keys[0])
        )
        
        for key in keys:
            if (keys[0] == key): continue
            
            binopt = ast.BinOp(
                left = binopt,
                op = ast.BitXor(),
                right = ast.Constant(value = key)
            )
        
        return binopt
    
    def generate_binopt_float(value: float, keys):
        obscured_value = value
        point_len = len(str(value).split('.')[1])
        
        for key in keys:
            obscured_value += key
            
        binopt = ast.BinOp(
            left = ast.Constant(value = obscured_value),
            op = ast.Sub(),
            right = ast.Constant(value = keys[0])
        )
        
        for key in keys:
            if (keys[0] == key): continue
            
            binopt = ast.BinOp(
                left = binopt,
                op = ast.Sub(),
                right = ast.Constant(value = key)
            )
            
        binopt = ast.Call(
            func=ast.Name(id='round'),
            args=[
                binopt,
                ast.Constant(value=point_len)
            ],
            keywords=[]
        )
        
        return binopt
    
    def proceed_int_constant(node: ast.Constant, ladder):
        keys = [random.randint(-0xFFFFFFFFF, 0xFFFFFFFFF) for _ in range(ladder)]
        name = Utils.randomize_name(MutatorUtils.alphabet, MutatorUtils.length)
        
        node = ast.Call(
                func=ast.Lambda(
                    args=ast.arguments(
                        posonlyargs=[],
                        args=[
                            ast.arg(arg=name)],
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[]),
                    body=ast.Call(
                        func=ast.Name(id=name),
                        args=[],
                        keywords=[])),
                args=[
                    ast.Lambda(
                        args=ast.arguments(
                            posonlyargs=[],
                            args=[],
                            kwonlyargs=[],
                            kw_defaults=[],
                            defaults=[]),
                        body=MutatorUtils.generate_binopt_int(node.value, keys))],
                keywords=[]
            )
        
        return node
    
    def proceed_float_constant(node: ast.Constant, ladder):
        keys = [random.uniform(0xFFFF, 0xFFFFFFFFF) for _ in range(ladder)]
        name = Utils.randomize_name(MutatorUtils.alphabet, MutatorUtils.length)
        
        node = ast.Call(
                func=ast.Lambda(
                    args=ast.arguments(
                        posonlyargs=[],
                        args=[
                            ast.arg(arg=name)],
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[]),
                    body=ast.Call(
                        func=ast.Name(id=name),
                        args=[],
                        keywords=[])),
                args=[
                    ast.Lambda(
                        args=ast.arguments(
                            posonlyargs=[],
                            args=[],
                            kwonlyargs=[],
                            kw_defaults=[],
                            defaults=[]),
                        body=MutatorUtils.generate_binopt_float(node.value, keys))],
                keywords=[]
            )
        
        return node
    

class NumberMutatorTransformer(Transformer):
    
    def __init__(self, ladder: int, safe_mode: bool, alphabet: str, length: int):
        self.ladder = ladder
        self.safe_mode = safe_mode
        MutatorUtils.safe_mode = safe_mode
        MutatorUtils.alphabet = alphabet
        MutatorUtils.length = length
        
    def proceed(self, tree: ast.Module):
        Logger.logger.name = __class__.__name__
        Logger.logger.info(f"transforming {self.__class__.__name__}...")
        
        self.tree = tree
        
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        num = NumberMutatorTransformer.NumberMutatorTransformer(self.tree,self.ladder, self.safe_mode)
        self.tree = num.visit(self.tree)
        
        return self.tree
    
    class NumberMutatorTransformer(ast.NodeTransformer):
        
        def __init__(self, tree, ladder: int, safe_mode: bool):
            self.tree = tree
            self.ladder = ladder
            self.safe_mode = safe_mode
        
        def visit_Assign(self, node: ast.Assign):
            if (isinstance(node.value, ast.Constant) and isinstance(node.value.value, int)):
                return MutatorUtils.proceed_int_assign(node, self.ladder)
            elif (isinstance(node.value, ast.List)):
                if (len(node.value.elts) == 0):
                    return node
                
                node = MutatorUtils.proceed_list_assign(node, self.ladder)
            
            return node
        
        def visit_Constant(self, node: ast.Constant):
            try:
                if (isinstance(node.parent, ast.MatchValue)):
                    return node
            except:
                return node
            
            if (isinstance(node.value, int)):
                return MutatorUtils.proceed_int_constant(node, self.ladder)
            elif (isinstance(node.value, float) and self.safe_mode == False):
                return MutatorUtils.proceed_float_constant(node, self.ladder)
            
            return node