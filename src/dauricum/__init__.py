"""

dauricum.

python 3.10+ obfuscator.

"""

__version__ = "1.0"
__author__ = 'nighty1337'

import io
import os
import time
import ast
from dauricum.tools.logger import Logger
from dauricum.transformers.renamer_transformer import RenamerTransformer
from dauricum.transformers.controlflow_transformer import ControlFlowTransformer
from dauricum.transformers.junk_transformer import JunkTransformer
from dauricum.transformers.exceptionjmp_transformer import ExceptionJumpTransformer
from dauricum.transformers.number_transformer import NumberMutatorTransformer
from dauricum.transformers.outline_transformer import OutlineTransformer
from dauricum.transformers.string_transformer import StringTransformer
from dauricum.transformers.call_transformer import CallTransformer
from dauricum.transformers.biopaque_transformer import BiOpaqueTransformer
from dauricum.transformers.function_transformer import FunctionTransformer
from dauricum.transformers.import_transformer import ImportTransformer
from dauricum.transformers.format_transformer import FormatTransformer


class ObfuscatorSettings:
    def __init__(self):
        self.transformers = []

    def add_transformer(self, transformer):
        self.transformers.append(transformer)

    def renamer_transformer(self, alphabet: str, length: int):
        self.add_transformer(RenamerTransformer(alphabet, length))

    def controlflow_transformer(self, ladder: int, alphabet: str, length: int, safe_mode: bool):
        self.add_transformer(ControlFlowTransformer(
            ladder, alphabet, length, safe_mode))

    def junk_transformer(self):
        self.add_transformer(JunkTransformer())

    def exceptionjmp_transformer(self, alphabet: str, length: int):
        self.add_transformer(ExceptionJumpTransformer(alphabet, length))

    def number_transformer(self, ladder: int, safe_mode: bool, alphabet: str, length: int):
        self.add_transformer(NumberMutatorTransformer(
            ladder, safe_mode, alphabet, length))

    def outline_transformer(self, alphabet: str, length: int):
        self.add_transformer(OutlineTransformer(alphabet, length))

    def string_transformer(self, alphabet: str, length: int):
        self.add_transformer(StringTransformer(alphabet, length))

    def call_transformer(self):
        self.add_transformer(CallTransformer())

    def biopaque_transformer(self):
        self.add_transformer(BiOpaqueTransformer())

    def function_transformer(self, alphabet: str, length: int):
        self.add_transformer(FunctionTransformer(alphabet, length))
    
    def import_transformer(self):
        self.add_transformer(ImportTransformer())
    
    def format_transformer(self):
        self.add_transformer(FormatTransformer())


class SizeCalculator:
    size_si = {0: "b", 1: "kb", 2: "mb", 3: "gb", 4: "tb"}

    def calculate_size_bytes(size: int):
        i = 0

        while size > 1024:
            size /= 1024
            i += 1

        return str(round(size)) + SizeCalculator.size_si.get(i)


class Obfuscator:
    def obfuscate(input_file: io.TextIOWrapper, out_file: io.TextIOWrapper, settings: ObfuscatorSettings):
        Logger.init(True, False)
        Logger.logger.name = __class__.__name__

        mb_size = os.stat(input_file.name).st_size
        Logger.logger.info(
            f"obfuscating \"{os.path.basename(input_file.name)}\" \033[90m(size: {SizeCalculator.calculate_size_bytes(mb_size)})\033[0m")

        start_time = time.time()

        tree = ast.parse(input_file.read())

        for transformer in settings.transformers:
            tree = transformer.proceed(tree)
        Logger.logger.name = __class__.__name__

        out_file.write(ast.unparse(tree))

        end_time = round(time.time() - start_time, 2)

        Logger.logger.info(
            f"obfuscated \"{os.path.basename(input_file.name)}\" in {end_time} seconds")
