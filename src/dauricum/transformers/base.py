from dauricum.tools.logger import Logger

class Transformer:
    def __init__(self):
        Logger.logger.name = __class__.__name__
    
    def proceed(self, tree):
        self.tree = tree
        Logger.logger.info(f"Transforming {self.__class__.__name__}...")
        
        return self.tree