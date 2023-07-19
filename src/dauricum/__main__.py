from dauricum import Obfuscator
from dauricum import ObfuscatorSettings
from dauricum.logger import Logger as Log
import argparse
    
def handle_args():
    description = "Python 3.10+ obfuscator with many obfuscation methods"
    parser = argparse.ArgumentParser(
        prog="dauricum",
        description=description
    )
    parser.add_argument(
        "-input",
        type=str,
        required=True,
        help="Path to target file",
    )
    parser.add_argument(
        "-output",
        type=str,
        required=True,
        help="Path to output file",
    )
    parser.add_argument(
        "--logging",
        type=bool,
        default=True,
        help="Log stuff"
    )
    parser.add_argument(
        "--mba-expression",
        action='store_true',
        help="Enables MBA Expression Transformer"
    )
    parser.add_argument(
        "--mba-expression-mode",
        type=bool,
        help="If true it will obfuscate numbers in expressions"
    )
    parser.add_argument(
        "--in-outline",
        action='store_true',
        help="Enables In Outline Transformer"
    )
    parser.add_argument(
        "--control-flow",
        action='store_true',
        help="Enables Control Flow Tranformer"
    )
    parser.add_argument(
        "--try-catch",
        action='store_true',
        help="Enables Try Catch Tranformer"
    )
    parser.add_argument(
        "--try-catch-mode",
        type=bool,
        help="If true it will enable safe mode"
    )
    parser.add_argument(
        "--try-catch-iter",
        type=int,
        default=1,
        help="Count of try-catch blocks in one function/if statement"
    )
    parser.add_argument(
        "--try-normalizer",
        action='store_true',
        help="Enables Try Normalizer Tranformer"
    )
    parser.add_argument(
        "--try-normalizer-iter",
        type=int,
        default=1,
        help="Count of ... in one try-catch block"
    )
    parser.add_argument(
        "--opaque",
        action='store_true',
        help="Enables Opaque Tranformer"
    )
    parser.add_argument(
        "--opaque-iter",
        type=int,
        default=1,
        help="Count of iterations"
    )
    parser.add_argument(
        "--rename",
        action='store_true',
        help="Enables Renamer Tranformer"
    )
    parser.add_argument(
        "--rename-mode",
        type=int,
        default=0,
        help="Change Renamer mode (0 - random sequence of 32 characters, 1 - random misleading word, 2 - random sequence of 64 characters, 3 - random word of misleading characters)"
    )
    
    args = parser.parse_args()
    return args

def main():
    args = handle_args()
    
    if (args.input == None or args.output == None):
        raise ValueError("Input or Output file is not specified!")
    
    input, output = open(args.input, "r", encoding="utf-8"), open(args.output, "w", encoding="utf-8")
    
    settings = ObfuscatorSettings()
    settings.setLoggerEnabled(args.logging)
    
    if (args.mba_expression):
        settings.MBAExpression(args.mba_expression_mode)
        
    if (args.rename):
        settings.Renamer(args.rename_mode)
        
    if (args.in_outline):
        settings.InOutline()
    
    if (args.opaque):
        settings.Opaque(args.opaque_iter)
        
    if (args.control_flow):
        settings.ControlFlow()
    
    if (args.try_catch):
        settings.TryCatch(args.try_catch_mode, args.try_catch_iter)
        
    if (args.try_normalizer):
        settings.TryNormalizer(args.try_normalizer_iter)
    
    Obfuscator.obfuscate(input, output, settings)
    
    if (not args.mba_expression and not args.in_outline
        and not args.control_flow and not args.try_catch
        and not args.try_normalizer):
        
        Log.logger.warning("No transformers are used!")
    
    input.close()
    output.close()

if __name__ == "__main__":
    main()