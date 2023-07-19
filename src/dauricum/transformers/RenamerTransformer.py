import ast, random, string, math, urllib3, enum
from dauricum.logger import Logger

class WordGenerator:
    def __init__(self, host):
        response = urllib3.request(method='GET', url=host)
        self.words = response.data.splitlines()
    def generate_random_word(self, capitalize = True):
        word = random.choice(self.words)
        if (capitalize):
            word = word.capitalize()
        
        return word.decode('utf8')

class NamingModes(enum.Enum):
    random32 = 0
    random64 = 2
    misleading = 1
    misleading_random = 3
    
class NameGenerator:
    word_generator = WordGenerator("https://www.mit.edu/~ecprice/wordlist.10000")
    
    def __init__(self, mode: NamingModes):
        self.mode = mode
    
    def generate_word_internal(self, length: int, chars: str):
        return ''.join(random.choice(chars) for _ in range(length))
    def generate_word(self):
        match self.mode:
            case NamingModes.random32: return ''.join(random.choice("abcdef01234") for i in range(32))
            case NamingModes.random64: return ''.join(random.choice("abcdef01234") for i in range(64))
            case NamingModes.misleading: return NameGenerator.word_generator.generate_random_word()
            case NamingModes.misleading_random: return ''.join(random.choice("βλπχΩΣΛΨΔ") for i in range(32))
        raise Exception("Undefined mode")

class RenamerController:
    function_mappings = {}
    field_mappings = {}
    class_mappings = {}

    def generate_name():
        generator = NameGenerator(RenamerTransformer.mode)
        word = generator.generate_word()
        
        while word[0].isdigit() or word in RenamerController.function_mappings.values() or word in RenamerController.field_mappings.values():
            word = generator.generate_word()
        
        return word
    
    def instantiate_parents(tree):
        i = 0
        
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
                child.position = i
                i+=1
    
    def find_field(tree, name, parent):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if (isinstance(child, ast.Assign)):
                    for target in child.targets:
                        if (isinstance(target, ast.Name)):
                            if (target.id == name):
                                return child
                        elif (isinstance(target, ast.Attribute)):
                            if (target.attr == name):
                                return child
                        else:
                            print("unsupported ", target)
        return None
    
    def find_class(tree, name):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if (isinstance(child, ast.ClassDef)):
                    if (child.name == name):
                        return child     
        return None
    
    def find_first_assign(tree, name):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if (isinstance(child, ast.Assign)):
                    for target in child.targets:
                        if (target.id == name):
                            return child
        return None
    def is_in_for(tree, node):
        parent = node.parent
        
        try:
            while 1:
                if (isinstance(parent, ast.For)): return parent
                
                parent = parent.parent
        except:
            return False
    def is_in_def(tree, node):
        parent = node.parent
        
        try:
            while 1:
                if (isinstance(parent, ast.FunctionDef)): return parent
                
                parent = parent.parent
        except:
            return False
    def is_in_class(tree, node):
        parent = node.parent
        
        try:
            while 1:
                if (isinstance(parent, ast.ClassDef)): return True
                
                parent = parent.parent
        except:
            return False
    
    def find_function(tree, name, parent):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if (isinstance(child, ast.FunctionDef)):
                    if (child.name == name):
                        return child
        return None

class RenamerTransformer:
    proceeded = 0
    proceeded_fields = 0
    tree = None
    mode = NamingModes.random32
    
    def __init__(self, tree, mode):
        Logger.logger.name = __class__.__name__
        self.tree = tree
        RenamerTransformer.tree = tree
        RenamerTransformer.mode = NamingModes(mode)
    def __init__(self, mode):
        Logger.logger.name = __class__.__name__
        self.tree = None
        RenamerTransformer.tree = None
        RenamerTransformer.mode = NamingModes(mode)
        
    def setTree(self, tree):
        self.tree = tree
        RenamerTransformer.tree = tree
    
    def proceed(self):
        Logger.logger.info(f"Transforming {self.__class__.__name__}...")
        
        RenamerController.instantiate_parents(self.tree)
        
        newTree = RenamerTransformer.RenamerTransformer().visit(self.tree)
        ast.fix_missing_locations(newTree)
        
        newTree = RenamerTransformer.FieldRenamerTransformer().visit(newTree)
        ast.fix_missing_locations(newTree)
        newTree = RenamerTransformer.FunctionRenamerTranformer().visit(newTree)
        ast.fix_missing_locations(newTree)
        newTree = RenamerTransformer.PreClassRenamerTransformer().visit(newTree)
        ast.fix_missing_locations(newTree)
        newTree = RenamerTransformer.ClassRenamerTransformer().visit(newTree)
        ast.fix_missing_locations(newTree)
        
        Logger.logger.info(f"Transformed: {RenamerTransformer.proceeded}")
        
        return newTree
    
    class RenamerTransformer(ast.NodeTransformer):
        def visit_FunctionDef(self, node: ast.FunctionDef):
            if (node.name.startswith("__")): return node
            
            generated_name = RenamerController.generate_name()
            RenamerController.function_mappings.update(
                {
                    node.name: generated_name
                }
            )
            
            node.name = generated_name
            
            RenamerTransformer.proceeded += 1
            
            return node
        def visit_Assign(self, node: ast.Assign):
            for target in node.targets:
                if (target.id.startswith("__")): return node
                if (RenamerController.is_in_class(RenamerTransformer.tree, node)): return node
            
                generated_name = RenamerController.generate_name()
                parent = node.parent
                
                RenamerController.field_mappings.update(
                    {
                        target.id + str(RenamerTransformer.proceeded_fields): [generated_name, parent, node, enumerate(RenamerController.field_mappings)]
                    }
                )
                
                node.targets[node.targets.index(target)].id = generated_name
                
                RenamerTransformer.proceeded_fields += 1
            
                RenamerTransformer.proceeded += 1
            
            return node

    class FunctionRenamerTranformer(ast.NodeTransformer):
        def visit_Name(self, node: ast.Name):
            if (node.id.startswith("__")): return node
            
            if (isinstance(node.parent, ast.Call) and not (node in node.parent.args)):
                for j in RenamerController.function_mappings.keys():
                    if (node.id == j):
                        node.id = RenamerController.function_mappings.get(node.id)
            elif (isinstance(node.parent, ast.Attribute) and isinstance(node.parent.parent, ast.Call)):
                for j in RenamerController.function_mappings.keys():
                    if (node.parent.attr == j):
                        found_field = RenamerController.find_field(RenamerTransformer.tree, node.parent.value.id, node.parent.parent.parent.parent)
                        
                        if (found_field != None):
                            if (isinstance(found_field.value, ast.Call)):
                                found_class = RenamerController.find_class(RenamerTransformer.tree, found_field.value.func.id)
                                
                                if (found_class != None):
                                    for bnode in found_class.body:
                                        if isinstance(bnode, ast.FunctionDef):
                                            found = RenamerController.function_mappings.get(j)
                                            
                                            if (found == bnode.name):
                                                node.parent.attr = found
            
            return node
    
    class FieldRenamerTransformer(ast.NodeTransformer):
        def visit_Name(self, node: ast.Name):
            
            i = 0
            is_for = RenamerController.is_in_for(RenamerTransformer.tree, node)
            
            if (is_for != False):
                iter = is_for.iter
                
                if (isinstance(iter, ast.Tuple)):
                    names = iter.elts
                    jj = 0
                    
                    for name in names:
                        for j in RenamerController.field_mappings.keys():
                            if j.startswith(name):
                                is_for.iter[jj] = RenamerController.field_mappings.get(j)[0]
                        jj += 1
                elif (isinstance(iter, ast.Name)):
                    name = iter.id
                    
                    for j in RenamerController.field_mappings.keys():
                        if j.startswith(name):
                            is_for.iter.id = RenamerController.field_mappings.get(j)[0]
                
                return node
            
            for j in RenamerController.field_mappings.keys():
                i += 1
                if (j.startswith(node.id)):
                    map = RenamerController.field_mappings.get(j)
                    
                    if (isinstance(node.parent, ast.Attribute)):
                        if (node.position > map[2].position):
                            node.id = map[0]
                    elif (isinstance(node.parent, ast.Call)):
                        if (node.position > map[2].position):
                            old = node.id
                            node.id = map[0]
                            ret = RenamerController.is_in_def(RenamerTransformer.tree, node)
                            
                            if (ret == False):
                                found = RenamerController.find_function(RenamerTransformer.tree, RenamerController.function_mappings.get(old), node.parent)
                                if (found != None):
                                    if (found.position > map[2].position):
                                        node.id = found.name
                                
                                return node
                            
                            for arg in ret.args.args:
                                if (arg.arg == old):
                                    node.id = old
                    elif (isinstance(node.parent, ast.FormattedValue)):
                        if (node.position > map[2].position):
                            node.id = map[0]
                    elif (isinstance(node.parent, ast.BinOp) and not (isinstance(node.parent.parent, ast.ListComp) or isinstance(node.parent.parent, ast.Lambda))):
                        if (node.position > map[2].position):
                            node.id = map[0]
                    elif (isinstance(node.parent, ast.Subscript)):
                        if (isinstance(node.parent.parent, ast.BinOp)):
                            if (node.position > map[2].position):
                                node.id = map[0]
                    elif (isinstance(node.parent, ast.comprehension)):
                        if (node.position > map[2].position and node.parent.iter == node):
                            node.id = map[0]
            
            return node
    
    class PreClassRenamerTransformer(ast.NodeTransformer): # Cannot rename attr due to bug in ast
        def visit_ClassDef(self, node: ast.ClassDef):
            if (node.name.startswith("_")): return node
            
            generated_name = RenamerController.generate_name()
            RenamerController.class_mappings.update(
                {
                    node.name: generated_name
                }
            )
            node.name = generated_name
            
            RenamerTransformer.proceeded += 1
            
            return node
    
    class ClassRenamerTransformer(ast.NodeTransformer):
        def visit_ClassDef(self, node: ast.ClassDef):
            for base in node.bases:
                if (isinstance(base, ast.Name)):
                    for j in RenamerController.class_mappings.keys():
                        if (j.startswith(base.id)):
                            base.id = RenamerController.class_mappings.get(j)
                elif (isinstance(base, ast.Attribute)):
                    for j in RenamerController.class_mappings.keys():
                        if (j.startswith(base.value.id)):
                            base.value.id = RenamerController.class_mappings.get(j)
            
            return node
        def visit_Call(self, node: ast.Call):
            for j in RenamerController.class_mappings.keys():
                if (isinstance(node.func, ast.Name)):
                    if (j.startswith(node.func.id)):
                        node.func.id = RenamerController.class_mappings.get(j)
            
            return node
        def visit_Attribute(self, node: ast.Attribute):
            for j in RenamerController.class_mappings.keys():
                if (isinstance(node.value, ast.Name)):
                    if (j.startswith(node.value.id)):
                        node.value.id = RenamerController.class_mappings.get(j)
                elif (isinstance(node.value, ast.Call)):
                    if (j.startswith(node.value.func.id)):
                        node.value.func.id = RenamerController.class_mappings.get(j)
            
            return node