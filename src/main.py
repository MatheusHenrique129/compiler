import sys
from lexicon_analyzer import LexiconAnalyzer
from syntax_analyzer import SyntaxAnalyzer

def read_file():
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        file_name = 'files/input02.pas'

    arq = open(file_name)
    buffer = arq.read()
    arq.close()

    return buffer

def main():
    buffer = read_file()
    lex = LexiconAnalyzer(buffer)
    parser = SyntaxAnalyzer(lex)
    
    try:
        parser.parse()
        print("Análise sintática concluída com sucesso.")
    except Exception as e:
        print(f"Erro na análise sintática: {str(e)}")

if __name__ == "__main__":
    main()