import ast, types, builtins, random, string
from dauricum.logger import Logger

" Inoutline Algorithm "

# TODO: Rewrite this shit code

default_names = [name for name, obj in vars(builtins).items() if not isinstance(obj, Exception)]

class AssignController:
    def getName():
        name = ''.join(random.choice(string.ascii_lowercase + (string.digits * 2)) for i in range(4, 24))
        
        while (name[0].isdigit()):
            name = ''.join(random.choice(string.ascii_lowercase + (string.digits * 2)) for i in range(4, 24))
        
        return name

    def generateLambdaForAssign(node : ast.Assign):
        args = []
        
        for node_2 in ast.walk(node):
            for child in ast.iter_child_nodes(node_2):
                child.parent = node_2
        
        class ArgVisitor(ast.NodeVisitor):
            def visit_Name(self, node : ast.Name):
                if ( not isinstance(node.parent, ast.Call) and not args.count(node.id) > 0 ):
                    args.append(node.id)
        ArgVisitor().visit(node.value)
        
        newArgs = []
        for i in args: 
            newArgs.append(ast.arg(arg=i))
        generatedName = AssignController.getName()
        
        return [ast.Assign(
            targets=[ ast.Name(id=generatedName, ctx=ast.Store() ) ],
            value=ast.Lambda(
                args=ast.arguments(
                    args=newArgs,
                    
                    posonlyargs=[],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[]
                ), 
                body=node.value
            ),
            lineno=None
        ), ast.Name(id=generatedName, ctx=ast.Store() ), newArgs]

class InOutlineTransformer:
    proceeded_assigns = 0
    proceeded_calls = 0
    assign_lambdas = {}
    call_lambdas = {}
    
    def __init__(self):
        Logger.logger.name = __class__.__name__
        self.tree = None
    def proceed(self):
        Logger.logger.info(f"Transforming {self.__class__.__name__}...")
        
        newTree = InOutlineTransformer.InOutlineTransformer().visit(self.tree)
        ast.fix_missing_locations(newTree)
        
        for assign_lambda_key in InOutlineTransformer.assign_lambdas:
            newTree.body.insert(0, InOutlineTransformer.assign_lambdas[assign_lambda_key][0])
        for call_lambdas_key in InOutlineTransformer.call_lambdas:
            newTree.body.insert(0, InOutlineTransformer.call_lambdas[call_lambdas_key])
        
        Logger.logger.info(f"Transformed Assigns: {InOutlineTransformer.proceeded_assigns}")
        Logger.logger.info(f"Transformed Calls: {InOutlineTransformer.proceeded_calls}")
        
        return newTree
        
    def setTree(self, tree):
        self.tree = tree
        
    class InOutlineTransformer(ast.NodeTransformer):
        def visit_Call(self, node : ast.Call):
            if (isinstance(node.func, ast.Attribute)):
                return node
            
            if (not node.func.id in default_names):
                return node
            
            if (not node.func.id in InOutlineTransformer.call_lambdas):
                InOutlineTransformer.call_lambdas.update( 
                    {
                        node.func.id: ast.Assign(
                            targets=[
                                ast.Name(id=AssignController.getName(), ctx=ast.Store())],
                            value=ast.Name(id=node.func.id, ctx=ast.Load()),
                            lineno=None
                        )
                    }
                )
            for call in InOutlineTransformer.call_lambdas:
                if (call == node.func.id):
                    node.func.id = InOutlineTransformer.call_lambdas[call].targets[0].id
            
            InOutlineTransformer.proceeded_calls += 1
            return node
        
        def visit_Assign(self, node : ast.Assign):
            if(isinstance(node, ast.AugAssign) or isinstance(node, ast.AnnAssign)): return node
            if (isinstance(node.value, ast.ListComp) or isinstance(node.value, ast.Lambda)):
                return node
            
            for target in node.targets:
                if(isinstance(target, ast.Attribute)): 
                    if (isinstance(target.value, ast.Name)):
                        if (target.value.id == 'self'):
                            return node
            
            class CallVisitor(ast.NodeVisitor):
                contains_call = False
                
                def visit_Call(self, node_2 : ast.Call):
                    if (not isinstance(node_2.func, ast.Name)): return node_2
                    try:
                        default_names.index(node_2.func.id)
                        return node_2
                    except:
                        CallVisitor.contains_call = True
                    CallVisitor.contains_call = True
                    return node_2
            
            CallVisitor().visit(node)
            if (CallVisitor.contains_call): return node
                
            for target in node.targets:
                InOutlineTransformer.assign_lambdas.update( 
                    {
                        target: AssignController.generateLambdaForAssign(node)
                    }
                )
                
            for lambda_key in InOutlineTransformer.assign_lambdas:
                if (InOutlineTransformer.assign_lambdas[lambda_key][0].value.body == node.value):
                    node.value = ast.Call(
                        func=InOutlineTransformer.assign_lambdas[lambda_key][1],
                        args=InOutlineTransformer.assign_lambdas[lambda_key][2],
                        keywords=[])
                    
                    break
            
            InOutlineTransformer.proceeded_assigns += 1
            return node