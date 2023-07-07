import ast, random, string, math
from dauricum.logger import Logger

"""

Control Flow using Match..Case construction (Python 3.10+)

- Example:

def func0():
    iter_var = 0
    
    while True:
        match iter_var:
            ...

"""

class ControlFlowController:
    def getChance():
        return random.randint(0, 1)
    def getName():
        name = ''.join(random.choice(string.ascii_lowercase + (string.digits * 2)) for i in range(4, 24))
        
        while (name[0].isdigit()):
            name = ''.join(random.choice(string.ascii_lowercase + (string.digits * 2)) for i in range(4, 24))
            
        return name
    def getRandomNonExistentValueFromArray(values, offset):
        v = 0
        while (v in values or v < len(values)) or v == 0:
            v = random.randint(1, len(values) * offset)
        
        return v
    
    def genCases(body, iterate_var):
        cases = []
        currentCase = 0
        casesValues = [0]
        
        offset = 3
        falseCases = 5
        
        # Real cases
        for line in body:
            casesValues.append(currentCase + offset)
            
            case = ast.match_case(
                    pattern=ast.MatchValue(
                        value=ast.Constant(value=currentCase)),
                    body=[
                        line,
                        ast.Assign(
                           targets=[
                                ast.Name(id=iterate_var, ctx=ast.Store())
                            ],
                            value=ast.Constant(value=currentCase + offset)
                        )
                    ]
                )
            if (currentCase == int(len(body)) * offset - offset):
                case.body.append(ast.Break())
            
            cases.append(
                case
            )
            
            currentCase += offset
        
        # Fake cases
        for i in range(falseCases):
            n = ControlFlowController.getRandomNonExistentValueFromArray(casesValues, offset)
            
            theMatch = ast.match_case(
                        pattern=ast.MatchValue(
                            value=ast.Constant(value=n)),
                        body=[ast.Assign(
                                targets=[
                                        ast.Name(id=iterate_var, ctx=ast.Store())
                                    ],
                                    value=ast.Constant(value=n)
                                )
                        ]
                    )

            if (bool(ControlFlowController.getChance())):
                for j in range(random.randint(1, 2)):
                    theMatch.body.append(ast.Break())
            
            cases.insert(round(n / 3), theMatch)
                
        # Finally, shuffle cases
        random.shuffle(cases)
            
        return cases

class ControlFlowTransformer:
    proceeded_defs = 0
    
    def __init__(self, tree):
        Logger.logger.name = __class__.__name__
        self.tree = tree
    def __init__(self):
        Logger.logger.name = __class__.__name__
        self.tree = None
        
    def setTree(self, tree):
        self.tree = tree
    
    def proceed(self):
        Logger.logger.info(f"Transforming {self.__class__.__name__}...")
        
        newTree = ControlFlowTransformer.BogusTransformer().visit(self.tree)
        ast.fix_missing_locations(newTree)
        
        Logger.logger.info(f"Transformed Functions: {ControlFlowTransformer.proceeded_defs}")
        
        return newTree
    
    class BogusTransformer(ast.NodeTransformer):
        def visit_FunctionDef(self, node: ast.FunctionDef):
            oldBody = node.body
            iterate_var = ControlFlowController.getName()
            
            definedVars = []
            
            for node_2 in oldBody:
                node_2._defined = False
            for node_2 in oldBody:
                if (isinstance(node_2, ast.Assign) and node_2._defined == False):
                    if (isinstance(node_2.targets[0], ast.Attribute)): 
                        continue
                    node_2._defined = True
                    
                    definedVars.append(ast.Assign(
                        targets=[
                            ast.Name(id=node_2.targets[0].id)],
                        value=ast.Constant(value=None),
                        lineno=None
                    ))
            
            node.body = []
            
            node.body.append(definedVars)
            
            node.body.append(ast.Assign(
                targets=[
                    ast.Name(id=iterate_var)],
                value=ast.Constant(value=0)))
            
            node.body.append( ast.While(
                test=ast.Constant(value=True),
                body=[
                    ast.Match(
                        subject=ast.Name(id=iterate_var),
                        cases=ControlFlowController.genCases(oldBody, iterate_var)
                    )
                ],
                orelse=[]))
            
            ControlFlowTransformer.proceeded_defs += 1
            return node