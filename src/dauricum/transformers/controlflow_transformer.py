
import ast, random
from dauricum.transformers.base import Transformer
from dauricum.tools.utils import Utils
from dauricum.tools.logger import Logger

class ControlFlowUtils:
    alphabet = "abcde01234"
    length = 16
    
    def generate_junk_controlflow_block(maps, max, node: ast.FunctionDef):
        cases = []
        
        for i in range(random.randint(0, 3)):
            num = random.randint(1, max)
            
            while (num in maps):
                num = random.randint(1, max)
            
            case_name = Utils.randomize_name(ControlFlowUtils.alphabet, ControlFlowUtils.length)
            case = ast.match_case(
                pattern=ast.MatchValue(
                    value=ast.Constant(value=num, parent = None)
                ),
                body=[
                    ast.Assign(
                        targets=[
                            ast.Name(id=case_name)
                        ],
                        value=ast.Constant(value=random.randint(0xFFFFF, 0xFFFFFFFFFFFF), parent = None),
                        lineno=None
                    )
                ]
            )
            
            fixed_body = node.body
            
            if (len(fixed_body) > 1):
                choice = random.choice(fixed_body)
                
                if isinstance(choice, ast.Global):
                    choice = ast.Pass
                elif isinstance(choice, list):
                    choice = ast.Pass
                for body_child in ast.walk(choice):
                    for body_child_child in ast.iter_child_nodes(body_child):
                        if isinstance(body_child_child, ast.Global):
                            body_child_child = ast.Pass
                            body_child = ast.Pass
                            choice = ast.Pass
                
                case.body.append(choice)
            
            cases.append(case)
        return cases
    
    def generate_controlflow_block(node):
        old_body = node.body
            
        current = Utils.generate_next_num(0, 0xFFFF)
        next_num = Utils.generate_next_num(current, 0xFFFFFFFFFFFFFF)
        maps = []
        global_list = []
        
        turn_name = Utils.randomize_name(ControlFlowUtils.alphabet, ControlFlowUtils.length)
        base = [
            ast.Assign(
                targets=[
                    ast.Name(id=turn_name)],
                value=ast.Constant(value=current),
                lineno=None),
            ast.While(
                test=ast.Compare(
                    left=ast.Name(id=turn_name),
                    ops=[
                        ast.Lt()],
                    comparators=[
                        ast.Constant(value=0xFFFFFFFFFFFFFF + 1)]),
                body=[
                    
                ],
                orelse=[]
            )
        ]
        
        new_base = ast.Match(
            subject=ast.Name(id=turn_name),
            cases=[]
        )
        
        for body_node in old_body:
            if isinstance(body_node, ast.Global):
                global_list.append(body_node)
                continue
            
            new = ast.match_case(
                pattern=ast.MatchValue(
                    value=ast.Constant(value=current)
                ),
                body=[
                    body_node
                ]
            )
            if (len(old_body) > 1):
                new.body.append(
                    ast.Assign(
                        targets=[
                            ast.Name(id=turn_name)
                        ],
                        value=ast.Constant(value=next_num),
                        lineno=None
                    )
                )
            
            new_base.cases.append(new)
            
            maps.append(next_num)
            current = next_num
            next_num = Utils.generate_next_num(current, 0xFFFFFFFFFFFFFFFF)
        base[1].test.comparators[0].value = next_num
        
        new_base.cases[len(new_base.cases) - 1].body.append(ast.Break())
        
        new_base.cases.append(ControlFlowUtils.generate_junk_controlflow_block(maps, next_num, node))
        
        random.shuffle(new_base.cases)
        
        base[1].body.append(
            new_base
        )
        for global_def in global_list:
            base.insert(0, global_def)
        
        node.body = base
    def generate_methods_clone(tree, node: ast.FunctionDef):
        methods = []
        
        random_body = None
        
        for _ in range(random.randint(0, 5)):
            while random_body == None:
                for _node in ast.walk(tree):
                    for _child in ast.iter_child_nodes(_node):
                        if (isinstance(_child, ast.FunctionDef)):
                            if (random.randint(0, 100) > 75):
                                random_body = _child.body
            
            empty_node = ast.FunctionDef(
                name=node.name,
                args=node.args,
                body=random_body,
                decorator_list=[],
                lineno=None)
            
            methods.append(
                empty_node
            )
            
            random_body = None
            
        methods.append(node)
        
        return methods

class ControlFlowTransformer(Transformer):
    
    def __init__(self, ladder: int, alphabet: str, length: int, safe_mode: bool):
        Logger.logger.name = __class__.__name__
        self.ladder = ladder
        self.safe_mode = safe_mode
        ControlFlowUtils.alphabet = alphabet
        ControlFlowUtils.length = length
    
    def proceed(self, tree: ast.Module):
        Logger.logger.name = __class__.__name__
        Logger.logger.info(f"transforming {self.__class__.__name__}...")
        
        self.tree = tree
        
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        flow = ControlFlowTransformer.ControlFlowTransformer()
        for i in range(self.ladder):
            self.tree = flow.visit(self.tree)
        flow = ControlFlowTransformer.ControlFlowPostTransformer(self.tree, self.safe_mode)
        self.tree = flow.visit(self.tree)
        
        return self.tree
    
    class ControlFlowTransformer(ast.NodeTransformer):
        
        def visit_FunctionDef(self, node: ast.FunctionDef):
            ControlFlowUtils.generate_controlflow_block(node)
            
            return node
    class ControlFlowPostTransformer(ast.NodeTransformer):
        
        def __init__(self, tree, ignore: bool):
            self.tree = tree
            self.ignore = ignore
        
        def visit_FunctionDef(self, node: ast.FunctionDef):
            if (self.ignore):
                node = ControlFlowUtils.generate_methods_clone(self.tree, node)
            
            return node