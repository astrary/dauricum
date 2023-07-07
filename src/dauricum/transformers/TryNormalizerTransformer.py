import ast, random, string, collections
from dauricum.logger import Logger

" Normalizes all exceptions "

class TryNormalizerController:
    def getChance():
        return random.randint(0, 100)
    def getName():
        name = ''.join(random.choice(string.ascii_lowercase + (string.digits * 2)) for i in range(4, 24))
        
        while (name[0].isdigit()):
            name = ''.join(random.choice(string.ascii_lowercase + (string.digits * 2)) for i in range(4, 24))
        
        return name
    def rngObject():
        return random.choice([random.randint(-2000000, 2000000), TryNormalizerController.getName()])
    
    def genBody(body_size):
        possibleOps = [ast.BitXor(), ast.BitOr(), ast.BitAnd()]
        body = []
        
        for i in range(body_size):
            chance = TryNormalizerController.getChance()
            
            if (chance > 0 and chance < 25):
                body.append(ast.Assign(targets=[ast.Name(id=TryNormalizerController.getName(), ctx=ast.Store())], value=ast.Constant(value=TryNormalizerController.rngObject()), lineno=None))
                chance = -1
            elif (chance > 25 and chance < 50):
                body.append(ast.FunctionDef(name=TryNormalizerController.getName(), args=ast.arguments(posonlyargs=[],
                    args=[], 
                    vararg=ast.arg(arg=TryNormalizerController.getName()), 
                    kwonlyargs=[], 
                    kw_defaults=[], 
                    defaults=[]), 
                    body=[ ast.Return(value=ast.BinOp( left = ast.Constant(value=random.randint(-2000000, 2000000)), 
                                    op = random.choice(possibleOps), right = ast.Constant(value=random.randint(-2000000, 2000000) )))], decorator_list=[], lineno=None ))
                chance = -1
            elif (chance > 50 and chance < 75):
                body.append(ast.Expr(value=ast.Constant(value=TryNormalizerController.getName())))
                chance = -1
            elif (chance > 75):
                body.append(ast.Expr(value=ast.BinOp(left=ast.Constant(value=random.randint(-2000000, 2000000)), op=random.choice(possibleOps), right=ast.Constant(value=random.randint(-2000000, 2000000)))))
                chance = -1
        
        return body

class TryNormalizierTransformer:
    proceeded_blocks = 0
    iterations = 0
    
    def __init__(self, tree, iterations):
        Logger.logger.name = __class__.__name__
        self.tree = tree
        TryNormalizierTransformer.iterations = iterations
    def __init__(self, iterations):
        Logger.logger.name = __class__.__name__
        self.tree = None
        TryNormalizierTransformer.iterations = iterations
        
    def setTree(self, tree):
        self.tree = tree
    
    def proceed(self):
        Logger.logger.info(f"Transforming {self.__class__.__name__}...")
        
        newTree = TryNormalizierTransformer.TryNormalizerTransformer().visit(self.tree)
        ast.fix_missing_locations(newTree)
        
        Logger.logger.info(f"Transformed Try blocks: {TryNormalizierTransformer.proceeded_blocks}")
        
        return newTree
    
    class TryNormalizerTransformer(ast.NodeTransformer):
        def visit_Try(self, node: ast.Try):
            if (not isinstance(node.body, collections.abc.Sequence)):
                node.body = [node.body]
            oldBody = node.body
            
            node.body = TryNormalizerController.genBody(TryNormalizierTransformer.iterations)
            node.body.append(oldBody)
            
            TryNormalizierTransformer.proceeded_blocks += 1
            return node