
import ast, random, sys
from dauricum.transformers.base import Transformer
from dauricum.tools.utils import Utils
from dauricum.tools.logger import Logger

sys.setrecursionlimit(15000)

class RenamerUtils:
    alphabet = "abcdefg01234"
    length = 16
    runtime_seed = random.randint(0xFFF, 0xFFFFFFFFFFFFFF)
    
    def randomize_name(original_name: str) -> str:
        seed = int(''.join(str(ord(chr)) for chr in original_name)) + RenamerUtils.runtime_seed
        random.seed(seed)
        
        name = ''.join([random.choice(RenamerUtils.alphabet) for _ in range(RenamerUtils.length)])
        while name[0].isdigit():
            name = ''.join([random.choice(RenamerUtils.alphabet) for _ in range(RenamerUtils.length)])
        
        return name
    
    def is_bad_name(name: str):
        bad_names = ['self', 'super']
        
        if name in bad_names or name.startswith("__"):
            return True
        return False
    
    def generate_funcdef_attribute(klass: ast.ClassDef, func_name: str):
        parent = klass.parent
        parents = [klass.name]
        
        while not isinstance(parent, ast.Module):
            parents.append(parent.name)
            
            parent = parent.parent
        
        parents.reverse()
        
        if len(parents) > 1:
            first_parent = parents.pop(0)
            
            attr = ast.Attribute(value=ast.Name(id=first_parent), attr=func_name)
            for _parent in parents:
                
                attr.value = ast.Attribute(value=attr.value, attr=_parent)
        else:
            attr = ast.Attribute(value=ast.Name(id=klass.name), attr=func_name)
        
        return attr
    
    def is_good_name(node: ast.Name | ast.Attribute, metadata):
        name = None
        subname = None
        good = False
        
        if isinstance(node, ast.Name):
            name = node.id
        elif isinstance(node, ast.Attribute):
            name = node.attr
            if isinstance(node.value, ast.Name):
                subname = node.value.id
            elif isinstance(node.value, ast.Attribute):
                subname = node.value.attr
        
        if name == None or name in metadata.imported_names or subname in metadata.imported_names:
            good = False
        
        return good

class RenamerTransformer(Transformer):
    
    def __init__(self, alphabet: str, length: int):
        RenamerUtils.alphabet = alphabet
        RenamerUtils.length = length
        
    def proceed(self, tree: ast.Module):
        Logger.logger.name = __class__.__name__
        Logger.logger.info(f"transforming {self.__class__.__name__}...")
        
        self.tree = tree
        self.old_random = random.getstate()
        
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        metadata = RenamerTransformer.MetadataVisitor()
        metadata.visit(self.tree)
        
        renamer = RenamerTransformer.RenamerTransformer(metadata)
        self.tree = renamer.visit(self.tree)
        
        random.setstate(self.old_random)
        
        return self.tree
    
    class MetadataVisitor(ast.NodeVisitor):
        def __init__(self):
            self.local_names = []
            self.imported_names = []
        
        def visit_Import(self, node: ast.Import):
            for name in node.names:
                self.imported_names.append(name.name)
                if name.asname != None:
                    self.imported_names.append(name.asname)
            
            return node
        
        def visit_ImportFrom(self, node: ast.ImportFrom):
            self.imported_names.append(node.module)
            for name in node.names:
                self.imported_names.append(name.name)
                if name.asname != None:
                    self.imported_names.append(name.asname)
            
            return node
        
        def visit_FunctionDef(self, node: ast.FunctionDef):
            if not RenamerUtils.is_bad_name(node.name):
                
                if isinstance(node.parent, ast.Module):
                    self.local_names.append(ast.Name(id=node.name))
                    self.local_names.append(node.name)
                elif isinstance(node.parent, ast.ClassDef):
                    value = RenamerUtils.generate_funcdef_attribute(node.parent, node.name)
                    
                    self.local_names.append(ast.Attribute(value=value, attr=node.name))
                    self.local_names.append(node.name)
                else:
                    return node
                self.local_names.append(node.name)
            
            
            for bnode in node.body:
                metadata = RenamerTransformer.MetadataVisitor()
                metadata.visit(bnode)
                for name in metadata.local_names:
                    self.local_names.append(name)
            
            for arg in node.args.args:
                self.local_names.append(arg.arg)
            
            return node
        
        def visit_Assign(self, node: ast.Assign):
            for name in node.targets:
                if isinstance(name, ast.Name):
                    self.local_names.append(name.id)
                    self.local_names.append(name)
                elif isinstance(name, ast.Attribute):
                    self.local_names.append(name.value)
                    self.local_names.append(name.attr)
                    self.local_names.append(name)
                elif isinstance(name, ast.Tuple):
                    for elt in name.elts:
                        self.local_names.append(elt)
                        if isinstance(elt, ast.Name):
                            self.local_names.append(elt.id)
                        elif isinstance(elt, ast.Attribute):
                            self.local_names.append(elt.attr)
            
            return node
        
        def visit_For(self, node: ast.For):
            for bnode in node.body:
                metadata = RenamerTransformer.MetadataVisitor()
                metadata.visit(bnode)
                for name in metadata.local_names:
                    self.local_names.append(name)
            
            if isinstance(node.target, ast.Name):
                self.local_names.append(node.target.id)
            elif isinstance(node.target, ast.Attribute):
                self.local_names.append(node.target.attr)
            if isinstance(node.iter, ast.Name):
                self.local_names.append(node.iter.id)
            elif isinstance(node.iter, ast.Attribute):
                self.local_names.append(node.iter.attr) 
                self.local_names.append(node.iter.value.id) 
            
            return node
        
        def visit_If(self, node: ast.If):
            for bnode in node.body:
                metadata = RenamerTransformer.MetadataVisitor()
                metadata.visit(bnode)
                for name in metadata.local_names:
                    self.local_names.append(name)
            for bnode in node.orelse:
                metadata = RenamerTransformer.MetadataVisitor()
                metadata.visit(bnode)
                for name in metadata.local_names:
                    self.local_names.append(name)
            
            return node
    
    class RenamerTransformer(ast.NodeTransformer):
        def __init__(self, metadata):
            self.metadata = metadata
            self.local_names = metadata.local_names
        
        def visit_Name(self, node: ast.Name):
            if not RenamerUtils.is_bad_name(node.id):
                if node in self.local_names:
                    node.id = RenamerUtils.randomize_name(node.id)
            
            return node
        
        def visit_Attribute(self, node: ast.Attribute):
            if not RenamerUtils.is_bad_name(node.attr):
                if node in self.local_names:
                    node.attr = RenamerUtils.randomize_name(node.attr)
            
            return node
        
        def visit_FunctionDef(self, node: ast.FunctionDef):
            if not RenamerUtils.is_bad_name(node.name):
                if node.name in self.local_names:
                    node.name = RenamerUtils.randomize_name(node.name)
            
            for bnode in node.body:
                renamer = RenamerTransformer.RenamerTransformer(self.metadata)
                bnode = renamer.visit(bnode)
            
            for arg in node.args.args:
                if not RenamerUtils.is_bad_name(arg.arg):
                    if arg.arg in self.local_names:
                        arg.arg = RenamerUtils.randomize_name(arg.arg)
            
            return node
        
        def visit_Lambda(self, node: ast.Lambda):
            for arg in node.args.args:
                new_arg = arg
                new_arg.arg = RenamerUtils.randomize_name(new_arg.arg)
                
                node.args.args[node.args.args.index(arg)] = new_arg
            
            return super().generic_visit(node)
        
        def visit_For(self, node: ast.For):
            for bnode in node.body:
                renamer = RenamerTransformer.RenamerTransformer(self.metadata)
                bnode = renamer.visit(bnode)
            for wnode in ast.walk(node):
                for bnode in ast.iter_child_nodes(wnode):
                    if isinstance(bnode, ast.For):
                        renamer = RenamerTransformer.RenamerTransformer(self.metadata)
                        bnode = renamer.visit_For(bnode)
            
            if isinstance(node.target, ast.Name):
                if not RenamerUtils.is_bad_name(node.target.id):
                    if node.target.id in self.local_names:
                        node.target.id = RenamerUtils.randomize_name(node.target.id)
            elif isinstance(node.target, ast.Attribute):
                if not RenamerUtils.is_bad_name(node.target.attr):
                    if node.target.attr in self.local_names:
                        node.target.attr = RenamerUtils.randomize_name(node.target.attr)
            elif isinstance(node.target, ast.Tuple):
                for elt in node.target.elts:
                    if isinstance(elt, ast.Name):
                        if not RenamerUtils.is_bad_name(elt.id):
                            if elt.id in self.local_names:
                                elt.id = RenamerUtils.randomize_name(elt.id)
                    elif isinstance(elt, ast.Attribute):
                        if not RenamerUtils.is_bad_name(elt.attr):
                            if elt.attr in self.local_names:
                                elt.attr = RenamerUtils.randomize_name(elt.attr)
            
            if isinstance(node.iter, ast.Name):
                if not RenamerUtils.is_bad_name(node.iter.id):
                    if node.iter.id in self.local_names:
                        node.iter.id = RenamerUtils.randomize_name(node.iter.id)
            elif isinstance(node.iter, ast.Attribute):
                if not RenamerUtils.is_bad_name(node.iter.attr):
                    if node.iter.attr in self.local_names:
                        node.iter.attr = RenamerUtils.randomize_name(node.iter.attr)
            elif isinstance(node.iter, ast.Call):
                for wnode in ast.walk(node.iter):
                    for bnode in ast.iter_child_nodes(wnode):
                        if isinstance(bnode, ast.Name):
                            if not RenamerUtils.is_bad_name(bnode.id):
                                if bnode.id in self.local_names:
                                    bnode.id = RenamerUtils.randomize_name(bnode.id)
                        elif isinstance(bnode, ast.Attribute):
                            if not RenamerUtils.is_bad_name(bnode.attr):
                                if bnode.attr in self.local_names:
                                    bnode.attr = RenamerUtils.randomize_name(bnode.attr)
            
            return node
        
        def visit_If(self, node: ast.If):
            for bnode in node.body:
                renamer = RenamerTransformer.RenamerTransformer(self.metadata)
                bnode = renamer.visit(bnode)
            for bnode in node.orelse:
                renamer = RenamerTransformer.RenamerTransformer(self.metadata)
                bnode = renamer.visit(bnode)
            
            for bnode in ast.walk(node.test):
                renamer = RenamerTransformer.RenamerTransformer(self.metadata)
                bnode = renamer.visit(bnode)
            
            return super().generic_visit(node)
        
        def visit_Assign(self, node: ast.Assign):
            if isinstance(node.value, ast.Name):
                if not RenamerUtils.is_bad_name(node.value.id):
                    if node.value.id in self.local_names:
                        node.value.id = RenamerUtils.randomize_name(node.value.id)
            elif isinstance(node.value, ast.Attribute):
                if not RenamerUtils.is_bad_name(node.value.attr):
                    if node.value.attr in self.local_names:
                        node.value.attr = RenamerUtils.randomize_name(node.value.attr)
        
            return super().generic_visit(node)
        
        def visit_Compare(self, node: ast.Compare):
            if isinstance(node.left, ast.Name):
                if not RenamerUtils.is_bad_name(node.left.id):
                    if node.left.id in self.local_names:
                        node.left.id = RenamerUtils.randomize_name(node.left.id)
            elif isinstance(node.left, ast.Attribute):
                if not RenamerUtils.is_bad_name(node.left.attr):
                    if node.left.attr in self.local_names:
                        node.left.attr = RenamerUtils.randomize_name(node.left.attr)
            
            for comparator in node.comparators:
                if isinstance(comparator, ast.Name):
                    if not RenamerUtils.is_bad_name(comparator.id):
                        if comparator.id in self.local_names:
                            comparator.id = RenamerUtils.randomize_name(comparator.id)
                elif isinstance(comparator, ast.Attribute):
                    if not RenamerUtils.is_bad_name(comparator.attr):
                        if comparator.attr in self.local_names:
                            comparator.attr = RenamerUtils.randomize_name(comparator.attr)
            
            return node
        
        def visit_AugAssign(self, node: ast.AugAssign):
            if isinstance(node.value, ast.Name):
                if not RenamerUtils.is_bad_name(node.value.id):
                    if node.value.id in self.local_names:
                        node.value.id = RenamerUtils.randomize_name(node.value.id)
            elif isinstance(node.value, ast.Attribute):
                if not RenamerUtils.is_bad_name(node.value.attr):
                    if node.value.attr in self.local_names:
                        node.value.attr = RenamerUtils.randomize_name(node.value.attr)

            if isinstance(node.target, ast.Name):
                if not RenamerUtils.is_bad_name(node.target.id):
                    if node.target.id in self.local_names:
                        node.target.id = RenamerUtils.randomize_name(node.target.id)
            elif isinstance(node.target, ast.Attribute):
                if not RenamerUtils.is_bad_name(node.target.attr):
                    if node.target.attr in self.local_names:
                        node.target.attr = RenamerUtils.randomize_name(node.target.attr)
        
            return super().generic_visit(node)
        
        def visit_Return(self, node: ast.Return):
            for wnode in ast.walk(node):
                for bnode in ast.iter_child_nodes(wnode):
                    if isinstance(bnode, ast.Name):
                        if not RenamerUtils.is_bad_name(bnode.id):
                            if bnode.id in self.local_names:
                                bnode.id = RenamerUtils.randomize_name(bnode.id)
                    elif isinstance(bnode, ast.Attribute):
                        if not RenamerUtils.is_bad_name(bnode.attr):
                            if bnode.attr in self.local_names:
                                bnode.attr = RenamerUtils.randomize_name(bnode.attr)
            
            return super().generic_visit(node)
        
        def visit_BinOp(self, node: ast.BinOp):
            for bnode in ast.walk(node):
                if isinstance(bnode, ast.Name):
                    if not RenamerUtils.is_bad_name(bnode.id):
                        if bnode.id in self.local_names:
                            bnode.id = RenamerUtils.randomize_name(bnode.id)
                elif isinstance(bnode, ast.Attribute):
                    if not RenamerUtils.is_bad_name(bnode.attr):
                        if bnode.attr in self.local_names:
                            bnode.attr = RenamerUtils.randomize_name(bnode.attr)
            
            return node
        
        def visit_Global(self, node: ast.Global):
            for name in node.names:
                ind = node.names.index(name)
                
                if not RenamerUtils.is_bad_name(name):
                    for lname in self.local_names:
                        if isinstance(lname, ast.Name):
                            if lname.id == name or lname.id == RenamerUtils.randomize_name(name):
                                node.names[ind] = RenamerUtils.randomize_name(name)
            
            return node
        
        def visit_comprehension(self, node: ast.comprehension):
            if isinstance(node.target, ast.Name):
                if not RenamerUtils.is_bad_name(node.target.id):
                    if node.target.id in self.local_names:
                        node.target.id = RenamerUtils.randomize_name(node.target.id)
            elif isinstance(node.target, ast.Attribute):
                if not RenamerUtils.is_bad_name(node.target.attr):
                    if node.target.attr in self.local_names:
                        node.target.attr = RenamerUtils.randomize_name(node.target.attr)
            if isinstance(node.iter, ast.Name):
                if not RenamerUtils.is_bad_name(node.iter.id):
                    if node.iter.id in self.local_names:
                        node.iter.id = RenamerUtils.randomize_name(node.iter.id)
            elif isinstance(node.iter, ast.Attribute):
                if not RenamerUtils.is_bad_name(node.iter.attr):
                    if node.iter.attr in self.local_names:
                        node.iter.attr = RenamerUtils.randomize_name(node.iter.attr)
            
            return node
        
        def visit_Call(self, node: ast.Call):
            name = None
            
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            
            if not RenamerUtils.is_bad_name(name):
                for localn in self.local_names:
                    if isinstance(localn, ast.Attribute) and isinstance(node.func, ast.Attribute):
                        if localn.attr == node.func.attr and not localn.attr in self.metadata.imported_names:
                            node.func.attr = RenamerUtils.randomize_name(node.func.attr)
                            if node.func.value.id in self.local_names:
                                node.func.value.id = RenamerUtils.randomize_name(node.func.value.id)
                    elif isinstance(localn, ast.Name) and isinstance(node.func, ast.Name):
                        if localn.id == node.func.id:
                            node.func.id = RenamerUtils.randomize_name(node.func.id)
            
            for arg in node.args:
                new_arg = arg
                
                for wnode in ast.walk(node):
                    for bnode in ast.iter_child_nodes(wnode):
                        if isinstance(bnode, ast.Name):
                            if not RenamerUtils.is_bad_name(bnode.id):
                                if bnode.id in self.local_names and not bnode.id in self.metadata.imported_names:
                                    bnode.id = RenamerUtils.randomize_name(bnode.id)
                        elif isinstance(bnode, ast.Attribute):
                            if not RenamerUtils.is_bad_name(bnode.attr):
                                if bnode.attr in self.local_names:
                                    bnode.attr = RenamerUtils.randomize_name(bnode.attr)
                        elif isinstance(bnode, ast.Lambda):
                            renamer = RenamerTransformer.RenamerTransformer(self.metadata)
                            bnode = renamer.visit(bnode)
                
                node.args[node.args.index(arg)] = new_arg
                    
            return node