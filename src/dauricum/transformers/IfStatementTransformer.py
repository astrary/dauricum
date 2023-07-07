import ast, random

" Packs Assign into If "

"""
- Example:

a = None

if (...):
    a = 2 + 2
else:
    throw Exception()

"""

class IfStatementTransformer:
    
    class IfStatementTransformer(ast.NodeTransformer):
        def visit_Assign(self, node: ast.Assign):
            return node