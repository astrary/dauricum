
import dauricum, argparse, rgbprint
from dauricum.tools.logger import Logger

def handle_args():
    description = "python 3.10+ obfuscator"
    
    parser = argparse.ArgumentParser(
        prog="dauricum",
        description=description
    )
    parser.add_argument(
        "-input",
        type=str,
        help="path to input file",
    )
    parser.add_argument(
        "-output",
        type=str,
        help="path to output file",
    )
    
    parser.add_argument(
        "--alphabet",
        type=str,
        default="abcdef01234",
        help="name generation alphabet"
    )
    parser.add_argument(
        "--alphabet-length",
        type=int,
        default=16,
        help="name generation alphabet length"
    )
    parser.add_argument(
        "--call-transformer",
        action='store_true',
        help="enables call transformer"
    )
    parser.add_argument(
        "--flow-transformer",
        action='store_true',
        help="enables control flow transformer"
    )
    parser.add_argument(
        "--flow-ladder",
        type=int,
        default=5,
        help="flow match-case ladder"
    )
    parser.add_argument(
        "--flow-safe",
        type=bool,
        default=False,
        help="flow safe mode"
    )
    parser.add_argument(
        "--excjmp-transformer",
        action='store_true',
        help="enables exception jump transformer"
    )
    parser.add_argument(
        "--function-transformer",
        action='store_true',
        help="enables function mutator transformer"
    )
    parser.add_argument(
        "--number-transformer",
        action='store_true',
        help="enables number mutator transformer"
    )
    parser.add_argument(
        "--number-ladder",
        type=int,
        default=7,
        help="number xor ladder"
    )
    parser.add_argument(
        "--number-safe",
        type=bool,
        default=True,
        help="ignore float"
    )
    parser.add_argument(
        "--outline-transformer",
        action='store_true',
        help="enables outline transformer"
    )
    parser.add_argument(
        "--renamer-transformer",
        action='store_true',
        help="enables renamer transformer"
    )
    parser.add_argument(
        "--string-transformer",
        action='store_true',
        help="enables string mutator transformer"
    )
    
    args = parser.parse_args()
    return args

class CommandLineInterface:
    
    def __init__(self, settings: dauricum.ObfuscatorSettings):
        self.settings = settings
    
    def hello(self):
        rgbprint.gradient_print("     __              _              \n ___/ /__ ___ ______(_)_____ ____ _ \n/ _  / _ `/ // / __/ / __/ // /  ' \\\n\\_,_/\\_,_/\\_,_/_/ /_/\\__/\\_,_/_/_/_/", start_color=0x4B79A1, end_color=0x283E51)
        rgbprint.gradient_print(f"version: {dauricum.__version__}".center(36), end_color=0x4B79A1, start_color=0x283E51)
        rgbprint.gradient_print(f"created by {dauricum.__author__}".center(36), end_color=0x4B79A1, start_color=0x283E51)
    
    def run(self):
        self.hello()
        print()
        
        rgbprint.gradient_print(f"input file path: ", end_color=0x2193b0, start_color=0x6dd5ed, end="")
        input_file = input()
        rgbprint.gradient_print(f"output file path: ", end_color=0x2193b0, start_color=0x6dd5ed, end="")
        output_file = input()
        
        rgbprint.gradient_print(f"name generation alphabet: ", end_color=0x2193b0, start_color=0x6dd5ed, end="")
        alphabet = input() or "abcde01234"
        rgbprint.gradient_print(f"name generation alphabet length: ", end_color=0x2193b0, start_color=0x6dd5ed, end="")
        alphabet_length = int(input() or 16)
        
        rgbprint.gradient_print(f"use outline transformer (y/n): ", end_color=0x2193b0, start_color=0x6dd5ed, end="")
        if input().lower().startswith("y"):
            self.settings.outline_transformer(alphabet, alphabet_length)
        
        rgbprint.gradient_print(f"use renamer transformer (y/n): ", end_color=0x2193b0, start_color=0x6dd5ed, end="")
        if input().lower().startswith("y"):
            self.settings.renamer_transformer(alphabet, alphabet_length)
        
        number_ladder = 7
        number_safe = True
        rgbprint.gradient_print(f"use number transformer (y/n): ", end_color=0x2193b0, start_color=0x6dd5ed, end="")
        if input().lower().startswith("y"):
            self.settings.number_transformer(number_ladder, number_safe, alphabet, alphabet_length)
        
        rgbprint.gradient_print(f"use string transformer (y/n): ", end_color=0x2193b0, start_color=0x6dd5ed, end="")
        if input().lower().startswith("y"):
            self.settings.string_transformer(alphabet, alphabet_length)
        
        flow_ladder = 5
        flow_safe = False
        rgbprint.gradient_print(f"use flow transformer (y/n): ", end_color=0x2193b0, start_color=0x6dd5ed, end="")
        if input().lower().startswith("y"):
            self.settings.controlflow_transformer(flow_ladder, alphabet, alphabet_length, flow_safe)
        
        rgbprint.gradient_print(f"use exception jump transformer (y/n): ", end_color=0x2193b0, start_color=0x6dd5ed, end="")
        if input().lower().startswith("y"):
            self.settings.exceptionjmp_transformer(alphabet, alphabet_length)
            
        rgbprint.gradient_print(f"use call transformer (y/n): ", end_color=0x2193b0, start_color=0x6dd5ed, end="")
        if input().lower().startswith("y"):
            self.settings.call_transformer()
            
        rgbprint.gradient_print(f"use function transformer (y/n): ", end_color=0x2193b0, start_color=0x6dd5ed, end="")
        if input().lower().startswith("y"):
            self.settings.function_transformer(alphabet, alphabet_length)
        
        return [self.settings, input_file, output_file]

def main():
    args = handle_args()
    
    settings = dauricum.ObfuscatorSettings()
    
    if (args.input == None or args.output == None):
        settings, input, output = CommandLineInterface(settings).run()
        input, output = open(input, "r", encoding="utf-8"), open(output, "w", encoding="utf-8")
    else:
        input, output = open(args.input, "r", encoding="utf-8"), open(args.output, "w", encoding="utf-8")
    
    if (args.outline_transformer):
        settings.outline_transformer(args.alphabet, args.alphabet_length)
    if (args.renamer_transformer):
        settings.renamer_transformer(args.alphabet, args.alphabet_length)
    if (args.number_transformer):
        settings.number_transformer(args.number_ladder, args.number_safe, args.alphabet, args.alphabet_length)
    if (args.string_transformer):
        settings.string_transformer(args.alphabet, args.alphabet_length)
    if (args.flow_transformer):
        settings.controlflow_transformer(args.flow_ladder, args.alphabet, args.alphabet_length, args.flow_safe)
    if (args.excjmp_transformer):
        settings.exceptionjmp_transformer(args.alphabet, args.alphabet_length)
    if (args.call_transformer):
        settings.call_transformer()
    if (args.function_transformer):
        settings.function_transformer(args.alphabet, args.alphabet_length)
        
    dauricum.Obfuscator.obfuscate(input, output, settings)