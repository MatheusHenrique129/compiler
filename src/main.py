################################################################################
# Avaliação Parcial 01 - Prof: Leonardo Massayuki Takuno                       #
#                                                                              #
# Bruna Tiemi Tarumoto Watanabe - 1904272                                      #
# Gustavo Goes Sant'Ana - 2201501                                              #
# Kaiky Amorim dos Santos - 2200387                                            #
# Matheus Henrique Santos da Silva - 2200973                                   #
################################################################################

from typing import NamedTuple
from typing import Union
import sys

ERROR = 0
IDENTIFIER = 1
NUM_INT = 2
NUM_REAL = 3
EOS = 4
RELOP = 5
ADDOP = 6
MULOP = 7

# palavras reservadas
IF = 8
THEN = 9
ELSE = 10
BEGIN = 11
END = 12
BOOLEAN = 13
DIV= 14
DO= 15
FALSE= 16
INTEGER= 17
MOD= 18
PROGRAM= 19
READ= 20
TRUE= 21
NOT= 22
VAR= 23
WHILE= 24
WRITE= 25
COMMENT = 26
PONTO_VIRG = 27
VIRGULA = 28
PARENTHESIS = 29
SUM = 30
SUB = 31
MULT = 32
DOT = 33

# operador relacional
LE = 1000
NE = 1001
LT = 1002
GE = 1003
GT = 1004
EQ = 1005

# Atomos
atomo_msg = ['Erro Sintático!', 'IDENTIFIER', 'NUM_INT   ', 'NUM_REAL', 'EOS',
             'RELOP', 'ADDOP', 'MULOP', 'IF', 'THEN', 'ELSE', 'BEGIN' , 'END',
             'BOOLEAN' ,'DIV','DO','FALSE','INTEGER','MOD','PROGRAM','READ',
             'TRUE','NOT','VAR','WHILE','WRITE', 'COMMENT', 'PONTO_VIRG', 'VIRGULA',
             'PARENTHESIS', 'SUM', 'SUB', 'MULT', 'DOT']

# Palavras reservadas
reserved_words = {'if': IF, 'then': THEN, 'else': ELSE, 'begin': BEGIN, 'end': END,
                  'boolean': BOOLEAN, 'div': DIV, 'do': DO, 'false': FALSE, 'integer': INTEGER, 
                  'mod': MOD, 'program': PROGRAM, 'read': READ, 'true': TRUE, 'not': NOT, 'var': VAR, 
                  'while': WHILE, 'write': WRITE, 'comment':COMMENT, 'ponto_virg':PONTO_VIRG, 
                  'virgula':VIRGULA, 'parenthesis': PARENTHESIS, 'sum': SUM, 'sub': SUB, 'mult': MULT, 'dot': DOT}

# Obj. Atomo
class Atomo(NamedTuple):
    type: int
    lexeme: str
    value: Union[int, float]
    operator: int
    line: int

# Analisador Lexico
class LexiconAnalyzer:
    def __init__(self, buffer: str):
        self.line = 1
        self.buffer = buffer + '\0'
        self.i = 0
    
    def next_char(self):
        c = self.buffer[self.i]
        self.i += 1
        return c
    
    def prev_char(self):
        self.i -= 1

    # analisador lexico dos atomos
    def next_atom(self):
        atomo = Atomo(ERROR, '', 0, 0, self.line)
        c = self.next_char()
        while (c in [' ', '\n', '\t', '\r', '\0']):
            if (c == '\n'):
                self.line += 1
            if (c == '\0'):
                return Atomo(EOS, '', 0, 0, self.line)
            c = self.next_char()     
        if c in ['/', '(', '{']:  
            comment = self.treat_comment(c)
            if comment:
                return comment
        if c.isalpha() or c == '_':
            return self.treat_identifier(c)
        elif c.isdigit():
            return self.treat_number(c)
        elif c== ':':
            nextChar=self.next_char()
            if nextChar == '=':
                return Atomo(RELOP,':=', 0, EQ, self.line)
            else:
                self.prev_char()
                return Atomo(RELOP,':',0, 0, self.line)
        elif c == '<' or c == '>':
            return self.treat_operator_minor(c)
        elif c in [';',',','(',')','.']:
            return Atomo(self.treat_punctuation(c), c, 0, 0, self.line)
        elif c in ['+','*','/','-']:
            return Atomo(self.treat_math_operation(c), c, 0, 0, self.line)
        return atomo

    # trata operadores maior, menor e igual
    def treat_operator_minor(self, c: str):
        c = self.next_char()
        state = 1
        while True:
            if state == 1:
                if c == '=':
                    state = 2
                elif c == '>':
                    state = 3
                else:
                    state = 4
            elif state == 2:
                return Atomo(RELOP, '<=', 0, LE, self.line)
            elif state == 3:
                return Atomo(RELOP, '<>', 0, NE, self.line)
            elif state == 4:
                self.prev_char()
                return Atomo(RELOP, '<', 0, LT, self.line)

    # trata os numeros
    def treat_number(self, c: str):
        lexeme = c
        c = self.next_char()
        state = 1
        while True:
            if state == 1:
                if c.isdigit():
                    lexeme += c
                    state = 1
                    c = self.next_char()
                else:
                    state = 2
            elif state == 2:
                self.prev_char()
                return Atomo(NUM_INT, lexeme, int(lexeme), 0, self.line)
    
    # trata identificadores
    def treat_identifier(self, c: str):
        lexeme = c
        c = self.next_char()
        state = 1
        while True:
            if state == 1:
                if c.isdigit() or c.isalpha() or c == '_':
                    lexeme += c
                    if len(lexeme) > 20:
                        return Atomo(ERROR, lexeme, 0, 0, self.line)
                    state = 1
                    c = self.next_char()
                else:
                    state = 2
            elif state == 2:
                self.prev_char()
                if lexeme.lower() in reserved_words:
                    reserved = reserved_words[lexeme.lower()]
                    return Atomo(reserved, lexeme, 0, 0, self.line)
                else:
                    return Atomo(IDENTIFIER, lexeme, 0, 0, self.line)

    # trata comentarios
    def treat_comment(self, initial: str):
        lexeme = initial
        # Trata Comentário de linha única, começando com //
        if initial == '/':
            nextChar = self.next_char()
            if nextChar == '/':
                lexeme += nextChar
                while True:
                    c = self.next_char()
                    if c == '\n' or c == '\0':
                        self.line += 1
                        break
                    lexeme += c
                return Atomo(COMMENT, lexeme, 0, 0, self.line)
            else:
                self.prev_char()  
                return None  

        # Trata Comentário de múltiplas linhas (*...*)
        elif initial == '(':
            nextChar = self.next_char()
            if nextChar == '*':
                lexeme += nextChar
                while True:
                    c = self.next_char()
                    if c == '\0':  # Chegou ao final do arquivo sem fechar o comentário
                        return Atomo(ERROR, lexeme, 0, 0, self.line)
                    if c == '\n':
                        self.line += 1
                    if c == '*' and self.next_char() == ')':
                        lexeme += '*)'
                        return Atomo(COMMENT, lexeme, 0, 0, self.line)
                    lexeme += c
            else:
                self.prev_char()  
                return None  

        # Trata Comentário de bloco {...}
        elif initial == '{':
            while True:
                c = self.next_char()
                if c == '\0':
                    return Atomo(ERROR, lexeme, 0, 0, self.line)
                lexeme += c
                if c == '\n':
                    self.line += 1
                if c == '}':
                    return Atomo(COMMENT, lexeme, 0, 0, self.line)
        
        return None  

    #trata pontuacao
    def treat_punctuation(self, c):
        if c == ';':
            return PONTO_VIRG
        if c == ',':
            return VIRGULA
        if c == '(' or c == ')':
            return PARENTHESIS
        if c == '.':
            return DOT

    #trata operadores matematicos
    def treat_math_operation(self, c):
        if c == '+':
            return SUM
        if c == '*':
            return MULT
        if c == '/':
            return DIV
        if c == '-':
            return SUB

# analizador sintaxico
class SyntaxAnalyzer:
    def __init__(self, lexicon_analyzer):
        self.lex = lexicon_analyzer
        self.lookahead = None

    def error(self, message):
        raise Exception(f"Erro sintático na linha {self.lookahead.line}: {message}")

    def consume(self, expected_type):
        self.handle_comment() # valida se tem um Comentário antes de consumir o atomo
        print(f'Linha: {self.lookahead.line} - átomo: {atomo_msg[self.lookahead.type]}\t\t lexema: {self.lookahead.lexeme}', end='')
        if self.lookahead.value != 0:
            print(f'\t\t valor: {self.lookahead.value}')
        else:
            print()

        if self.lookahead.type == expected_type:
            self.lookahead = self.lex.next_atom()
            self.handle_comment() # valida se o proximo atomo é um Comentário
        else:
            self.error(f"Esperado [ {atomo_msg[expected_type]} ], encontrado [ {atomo_msg[self.lookahead.type]} ]")

    def synthetic(self):
        self.lookahead = self.lex.next_atom()
        self.program()

    def handle_comment(self):
        while self.lookahead.type == COMMENT:
            self.lookahead = self.lex.next_atom()

    def program(self):
        self.consume(PROGRAM)
        self.consume(IDENTIFIER)
        if self.lookahead.type == PARENTHESIS and self.lookahead.lexeme == '(':
            self.consume(PARENTHESIS)
            self.list_identifiers()
            self.consume(PARENTHESIS)
        self.consume(PONTO_VIRG)
        self.block()
        self.consume(DOT)

    def block(self):
        if self.lookahead.type == VAR:
            self.variable_declarations()
        self.compound_command()

    def variable_declarations(self):
        self.consume(VAR)
        self.declaration()
        self.consume(PONTO_VIRG)
        while self.lookahead.type == IDENTIFIER:
            self.declaration()
            self.consume(PONTO_VIRG)

    def declaration(self):
        self.list_identifiers()
        self.consume(RELOP)  # ':=' é um RELOP
        self.type_declaration()

    def list_identifiers(self):
        self.consume(IDENTIFIER)
        while self.lookahead.type == VIRGULA:
            self.consume(VIRGULA)
            self.consume(IDENTIFIER)

    def type_declaration(self):
        if self.lookahead.type == INTEGER:
            self.consume(INTEGER)
        elif self.lookahead.type == BOOLEAN:
            self.consume(BOOLEAN)
        else:
            self.error("Tipo inválido")

    def compound_command(self):
        self.consume(BEGIN)
        self.command()
        while self.lookahead.type == PONTO_VIRG:
            self.consume(PONTO_VIRG)
            self.command()
        self.consume(END)

    def command(self):
        if self.lookahead.type == IDENTIFIER:
            self.assignment()
        elif self.lookahead.type == READ:
            self.input_command()
        elif self.lookahead.type == WRITE:
            self.output_command()
        elif self.lookahead.type == IF:
            self.command_if()
        elif self.lookahead.type == WHILE:
            self.command_while()
        elif self.lookahead.type == BEGIN:
            self.compound_command()
        else:
            self.error("Comando inválido")

    def assignment(self):
        self.consume(IDENTIFIER)
        self.consume(RELOP)  # ':=' é um RELOP
        self.expression()

    def command_if(self):
        self.consume(IF)
        self.expression()
        self.consume(THEN)
        self.command()
        if self.lookahead.type == ELSE:
            self.consume(ELSE)
            self.command()

    def command_while(self):
        self.consume(WHILE)
        self.expression()
        self.consume(DO)
        self.command()

    def input_command(self):
        self.consume(READ)
        self.consume(PARENTHESIS)
        self.list_identifiers()
        self.consume(PARENTHESIS)

    def output_command(self):
        self.consume(WRITE)
        self.consume(PARENTHESIS)
        self.expression()
        while self.lookahead.type == VIRGULA:
            self.consume(VIRGULA)
            self.expression()
        self.consume(PARENTHESIS)

    def expression(self):
        self.simple_expression()
        if self.lookahead.type == RELOP:
            self.consume(RELOP)
            self.simple_expression()

    def simple_expression(self):
        if self.lookahead.type in [SUM, SUB]:
            self.consume(self.lookahead.type)
        self.term()
        while self.lookahead.type in [SUM, SUB, ADDOP]:
            self.consume(self.lookahead.type)
            self.term()

    def term(self):
        self.factor()
        while self.lookahead.type in [MULT, DIV, MOD]:
            self.consume(self.lookahead.type)
            self.factor()

    def factor(self):
        if self.lookahead.type == IDENTIFIER:
            self.consume(IDENTIFIER)
        elif self.lookahead.type in [NUM_INT, NUM_REAL]:
            self.consume(self.lookahead.type)
        elif self.lookahead.type == PARENTHESIS and self.lookahead.lexeme == '(':
            self.consume(PARENTHESIS)
            self.expression()
            self.consume(PARENTHESIS)
        elif self.lookahead.type == TRUE:
            self.consume(TRUE)
        elif self.lookahead.type == FALSE:
            self.consume(FALSE)
        elif self.lookahead.type == NOT:
            self.consume(NOT)
            self.factor()
        else:
            self.error("Fator inválido")

# le o arquivo
def read_file():
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        file_name = 'files/error_case.txt'

    arq = open(file_name)
    buffer = arq.read()
    arq.close()

    return buffer

def main():
    buffer = read_file()
    lex = LexiconAnalyzer(buffer)
    synthetic = SyntaxAnalyzer(lex)

    try:
        synthetic.synthetic()
        print(f"{synthetic.lex.line} linhas analisadas, análise léxica e sintática concluída com sucesso.")
    except Exception as e:
        print(f"Erro: {str(e)}")
    
main()