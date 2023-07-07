from _ast import If
import ast, random, math
from typing import Any
from dauricum.logger import Logger

" Covers function's and if-statement's body into try-catch block "

class ArgsRandomizer:
    MAX_VALUE = 512512
    MIN_VALUE = 256
        
    def generate(max_root):
        possibleOps = [ast.BitXor(), ast.BitOr(), ast.BitAnd(), ast.LShift(), ast.RShift()] # Unsafe - ast.Mod() & ast.FloorDiv()
        # ast.UnaryOp() is only one direction operand!
        
        generatedOps = []
        currentRootSize = 0
        
        for op in range(2):
            currentOpLeft = ast.BinOp( left = ast.Constant(value = random.randint(ArgsRandomizer.MIN_VALUE, ArgsRandomizer.MAX_VALUE)), 
                                    op = random.choice(possibleOps), right = ast.Constant(value = random.randint(ArgsRandomizer.MIN_VALUE, ArgsRandomizer.MAX_VALUE)) )
            currentOpRight = ast.BinOp( left = ast.Constant(value = random.randint(ArgsRandomizer.MIN_VALUE, ArgsRandomizer.MAX_VALUE)), 
                                    op = random.choice(possibleOps), right = ast.Constant(value = random.randint(ArgsRandomizer.MIN_VALUE, ArgsRandomizer.MAX_VALUE)) )
            currentRootSize = max_root
            for root in range(currentRootSize):
                currentOpLeft = ast.BinOp( left = currentOpLeft, 
                                    op = random.choice(possibleOps), right = currentOpRight )
                currentOpRight = ast.BinOp( left = currentOpRight, 
                                    op = random.choice(possibleOps), right = currentOpLeft )
            generatedOps.append(ast.BinOp( left = currentOpLeft, 
                                op = random.choice(possibleOps), right = currentOpRight ))
        
        return ast.BinOp( left = generatedOps[0], 
                                    op = random.choice(possibleOps), right = generatedOps[1] )
class ExceptionRandomizer:
    def generate():
        return random.choice(["Exception", "OSError", "ValueError", "BlockingIOError", "ChildProcessError", "ConnectionError", "BrokenPipeError", "ConnectionAbortedError", "ConnectionRefusedError", "ConnectionResetError", "FileExistsError", "FileNotFoundError", "InterruptedError", "IsADirectoryError", "NotADirectoryError", "PermissionError", "ProcessLookupError", "TimeoutError"])

class TryBlock:
    def __init__(self, body):
        self.body = body
        self.args = [ast.Constant(value="null")]
    def random(self):
        self.args = [ArgsRandomizer.generate(2)] # Exception args size
    def get(self):
        body = ast.Raise(exc = ast.Call(func=ast.Name(id=ExceptionRandomizer.generate(), ctx=ast.Load()), args=self.args, keywords=[] ))
        
        return ast.Try(body = body, handlers = [ast.ExceptHandler(body = self.body)], orelse=None, finalbody = None)

class TryCatchTransformer:
    safe_mode = True
    proceeded_methods = 0
    proceeded_ifstatements = 0
    
    def __init__(self, tree, safe_mode, iterations):
        Logger.logger.name = __class__.__name__
        self.tree = tree
        self.iterations = iterations
        TryCatchTransformer.safe_mode = safe_mode
    def __init__(self, safe_mode, iterations):
        Logger.logger.name = __class__.__name__
        self.tree = None
        self.iterations = iterations
        TryCatchTransformer.safe_mode = safe_mode
    
    def setTree(self, tree):
         self.tree = tree
    
    def proceed(self):
        Logger.logger.info(f"Transforming {self.__class__.__name__}...")
        
        for i in range(self.iterations):
            newTree = TryCatchTransformer.TryCatchTransformer().visit(self.tree)
            ast.fix_missing_locations(newTree)
        
        Logger.logger.info(f"Transformed methods: {math.ceil(TryCatchTransformer.proceeded_methods / self.iterations)}")
        Logger.logger.info(f"Transformed if-statements: {math.ceil(TryCatchTransformer.proceeded_ifstatements / self.iterations)}")
        
        return newTree

    class TryCatchTransformer(ast.NodeTransformer):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
            if (node.name == '__init__'):
                return node
            if (TryCatchTransformer.safe_mode):
                for child in node.body:
                    if (isinstance(child, ast.Return)):
                        return node # Safe mode for catching
            block = TryBlock(node.body)
            block.random()
            
            node.body = [block.get()]
            
            TryCatchTransformer.proceeded_methods += 1
            return node
        
        def visit_If(self, node: If) -> Any:
            if (TryCatchTransformer.safe_mode):
                for child in node.body:
                    if (isinstance(child, ast.Return)):
                        return node # Safe mode for catching
            block = TryBlock(node.body)
            block.random()
            
            node.body = [block.get()]
            
            TryCatchTransformer.proceeded_ifstatements =+ 1
            return node