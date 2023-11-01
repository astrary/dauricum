
import ast, random
from dauricum.transformers.base import Transformer
from dauricum.tools.utils import Utils
from dauricum.tools.logger import Logger

class StaticValues:
    alphabet = ""
    length = 0
    runtime_seed = random.randint(0xFFF, 0xFFFFFFFFFFFFFF)

class Utils:
    def randomize_name(original_name: str, alphabet: str, length: int) -> str:
        seed = int(''.join(str(ord(chr)) for chr in original_name)) + StaticValues.runtime_seed
        random.seed(seed)
        
        name = ''.join([random.choice(alphabet) for _ in range(length)])
        while name[0].isdigit():
            name = ''.join([random.choice(alphabet) for _ in range(length)])
        
        return name
    
    def find_node_name(tree: ast.Module, name: str, orig_name: str):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if (isinstance(child, ast.Assign)):
                    for target in child.targets:
                        if isinstance(target, ast.Name):
                            if (target.id == name):
                                return target.id
                elif (isinstance(child, ast.For)):
                    if isinstance(child.target, ast.Tuple):
                        for elt in child.target.elts:
                            if isinstance(elt, ast.Name):
                                if (elt.id == Utils.randomize_name(orig_name, StaticValues.alphabet, StaticValues.length)):
                                    return elt.id
                    else:
                        if (child.target.id == Utils.randomize_name(orig_name, StaticValues.alphabet, StaticValues.length)):
                            return child.target.id
        return None
    
    def is_name_imported(tree: ast.Module, name: str):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if (isinstance(child, ast.ImportFrom)):
                    if child.module == name:
                        return True
                        
                    for name_a in child.names:
                        if name_a.name == name:
                            return True
                if (isinstance(child, ast.ImportFrom)):
                    pass
        return False
    
    def find_parent(node, target):
        parent = node
        
        while not isinstance(parent, target):
            if (isinstance(parent, ast.Module)):
                return None
            parent = parent.parent
        return parent
    
    def fix_renamer_function_args(tree: ast.Module):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if (isinstance(child, ast.Call)):
                    found_function = Utils.find_parent(child, ast.FunctionDef)
                    
                    if (not found_function): continue
                    for arg in found_function.args.args:
                        if (isinstance(child.func, ast.Name)):
                            if (arg.arg == Utils.randomize_name(child.func.id, StaticValues.alphabet, StaticValues.length)):
                                child.func.id = arg.arg

class RenamerTransformer(Transformer):
    
    def __init__(self, alphabet: str, length: int):
        StaticValues.alphabet = alphabet
        StaticValues.length = length
    
    def proceed(self, tree: ast.Module):
        Logger.logger.name = __class__.__name__
        Logger.logger.info(f"transforming {self.__class__.__name__}...")
        
        self.tree = tree
        self.old_random = random.getstate()
        
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        renamer = RenamerTransformer.FieldRenamerTransformer(tree)
        self.tree = renamer.visit(self.tree)
        Utils.fix_renamer_function_args(self.tree)
        
        renamer_functions = RenamerTransformer.FunctionRenamerTransformer()
        self.tree = renamer_functions.visit(self.tree)
        renamer_functions_post = RenamerTransformer.FunctionRenamerPostTransformer(renamer_functions.mappings)
        self.tree = renamer_functions_post.visit(self.tree)
        
        random.setstate(self.old_random)
        
        return self.tree
    
    class FunctionRenamerTransformer(ast.NodeTransformer):
        
        def __init__(self):
            self.mappings = {}
            self.bad_names = ["self", "super"]
        
        def visit_FunctionDef(self, node: ast.FunctionDef):
            new_name = Utils.randomize_name(node.name, StaticValues.alphabet, StaticValues.length)
            
            self.mappings.update({node.name: new_name})
            
            if (not node.name.startswith("__") and not node.name in self.bad_names):
                node.name = new_name
            
            return node
    class FunctionRenamerPostTransformer(ast.NodeTransformer):
        
        def __init__(self, mappings):
            self.mappings = mappings
            self.bad_names = ["self", "super"]
            
        def visit_Call(self, node: ast.Call):
            is_class_parent = isinstance(node.func, ast.Attribute)
            have_mapping = False
            if (isinstance(node.func, ast.Lambda)):
                return node
            
            if is_class_parent:
                if (not isinstance(node.func.value, ast.Call) or not isinstance(node.func.value.func, ast.Name)):
                    return node
                if isinstance(node.func.value, ast.Call) and node.func.value.func.id in self.bad_names:
                    return node
                
                have_mapping = node.func.attr in self.mappings.keys()
                
                if have_mapping:
                    node.func.attr = self.mappings.get(node.func.attr)
            else:
                # Fix ignoring ast.Call in ast.Call bug
                for node_child in ast.walk(node):
                    for child in ast.iter_child_nodes(node_child):
                        if (isinstance(child, ast.Call) and not isinstance(child.func, ast.Lambda)):
                            if isinstance(child.func, ast.Attribute):
                                have_mapping = child.func.attr in self.mappings.keys()
                
                                if have_mapping:
                                    child.func.attr = self.mappings.get(child.func.attr)
                            else:
                                have_mapping = child.func.id in self.mappings.keys()
                
                                if have_mapping:
                                    child.func.id = self.mappings.get(child.func.id)
                
                if isinstance(node.func, ast.Name):
                    have_mapping = node.func.id in self.mappings.keys()
                    
                    if have_mapping:
                        node.func.id = self.mappings.get(node.func.id)
            
            return node
    
    class FieldRenamerTransformer(ast.NodeTransformer):
        
        def __init__(self, tree: ast.Module):
            self.mappings = {}
            self.bad_names = ["self"]
            
            self.tree = tree
            
        def visit_arg(self, node: ast.arg):
            if (not node.arg.startswith("__") and not node.arg in self.bad_names):
                node.arg = Utils.randomize_name(node.arg, StaticValues.alphabet, StaticValues.length)
            
            return node
            
        def visit_Name(self, node: ast.Name):
            
            if (not node.id.startswith("__") and not node.id in self.bad_names
                and not (isinstance(node.parent, ast.Call) and node.parent.func == node)
                and not (isinstance(node.parent, ast.Assign) and isinstance(node.parent.value, ast.Lambda))
                and not isinstance(node.parent, ast.arg)
                and not isinstance(node.parent, ast.ClassDef)
                and not isinstance(node.parent, ast.ExceptHandler)
                and not isinstance(node.parent, ast.withitem)):
                
                if (not isinstance(node.parent, ast.Attribute)):
                    new_value = Utils.randomize_name(node.id, StaticValues.alphabet, StaticValues.length)
                    
                    # if Utils.find_parent(node, ast.withitem):
                    #     return node
                    if Utils.is_name_imported(self.tree, node.id):
                        return node
                    
                    self.mappings.update({node.id: new_value})
                    node.id = new_value
                else:
                    obscured_name = self.mappings.get(node.id)
                    
                    if (obscured_name != None):
                        found_node_name = Utils.find_node_name(self.tree, obscured_name, node.id)
                        
                        if (found_node_name != None):
                            node.id = found_node_name
            
            return node
        def visit_withitem(self, node: ast.withitem):
            
            if isinstance(node.context_expr, ast.Call):
                for arg in node.context_expr.args:
                    if isinstance(arg, ast.Name):
                        arg.id = Utils.randomize_name(arg.id, StaticValues.alphabet, StaticValues.length)
            
            
                if node.optional_vars != None:
                    for body in node.parent.body:
                        for body_node in ast.walk(body):
                            for child in ast.iter_child_nodes(body_node):
                                if isinstance(child, ast.Attribute):
                                    #print(ast.dump(child) + " 1")
                                    if node.optional_vars.id == child.value.id:
                                        child.value.id = Utils.randomize_name(child.value.id, StaticValues.alphabet, StaticValues.length)
                                    
                                # if isinstance(body_node, ast.Attribute):
                                #     if node.optional_vars.id == body_node.value.id:
                                #         print('got2 ' + body_node.value.id)
                    
                    #self.mappings.update({node.optional_vars.id: Utils.randomize_name(node.optional_vars.id, StaticValues.alphabet, StaticValues.length)})
                    node.optional_vars.id = Utils.randomize_name(node.optional_vars.id, StaticValues.alphabet, StaticValues.length)
                
            return node
