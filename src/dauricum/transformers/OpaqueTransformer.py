import ast, random
from dauricum.logger import Logger

" Packs Assign into If "

"""
- Example:

a = None

if (...):
    a = 2 + 2
else:
    throw Exception()

"""

class OpaqueTransformer:
    proceeded_assigns = 0
    
    def __init__(self, iterations: int):
        Logger.logger.name = __class__.__name__
        self.tree = None
        self.iterations = iterations
         
    def setTree(self, tree):
        self.tree = tree
      
    def proceed(self):
        Logger.logger.info(f"Transforming {self.__class__.__name__}...")
       
        for i in range(self.iterations):
            self.tree = OpaqueTransformer.OpaqueTransformer().visit(self.tree)
            ast.fix_missing_locations(self.tree)
       
        Logger.logger.info(f"Transformed assigns: {OpaqueTransformer.proceeded_assigns}")
       
        return self.tree
    
    class OpaqueTransformer(ast.NodeTransformer):
        def visit_Assign(self, node: ast.Assign):
            rng_number = random.randint(-255, 255)
            
            node = ast.If(
                test=ast.BinOp(
                    left=ast.BinOp(
                    left=ast.BinOp(
                        left=ast.Constant(value=rng_number),
                        op=ast.Sub(),
                        right=ast.BinOp(
                            left=ast.UnaryOp(
                                op=ast.Invert(),
                                operand=ast.Constant(value=rng_number)),
                            op=ast.Mult(),
                            right=ast.Constant(value=2))),
                    op=ast.Sub(),
                    right=ast.BinOp(
                        left=ast.Constant(value=rng_number),
                        op=ast.Sub(),
                        right=ast.UnaryOp(
                            op=ast.Invert(),
                            operand=ast.Constant(value=rng_number)))),
                    op=ast.Sub(),
                    right=ast.Constant(value=rng_number)),
                body=[
                    ast.Expr(
                    value=node)],
                orelse=[
                    ast.Expr(
                        value=ast.List(
                            elts=[
                            ast.BinOp(
                                left=ast.Constant(value='catch me if you can'),
                                op=ast.Mult(),
                                right=ast.Constant(value=random.randint(0xFFFFFFFFFFF, 0xFFFFFFFFFFFFF)))],
                            ctx=ast.Load()))])
            
            OpaqueTransformer.proceeded_assigns += 1
            return node