import dauricum

def run():
    settings = dauricum.ObfuscatorSettings()
    alphabet = "_liI"
    length = 16
    
    input, output = open("examples/example-unobfuscated.py", "r", encoding="utf-8"), open("examples/example-obfuscated.py", "w", encoding="utf-8")
    
    settings.import_transformer()
    settings.format_transformer()
    settings.outline_transformer(alphabet, length)
    settings.renamer_transformer(alphabet, length)
    settings.number_transformer(7, True, alphabet, length)
    settings.controlflow_transformer(5, alphabet, length, False)
    settings.exceptionjmp_transformer(alphabet, length)
    settings.string_transformer(alphabet, length)
    settings.call_transformer()
    settings.function_transformer(alphabet, length)
    
    dauricum.Obfuscator.obfuscate(input, output, settings)

if __name__ == "__main__":
    run()