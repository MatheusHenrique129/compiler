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
PARENTESES = 29
SUM = 30
SUB = 31
MULT = 32
PONTO = 33


# operador relacional
LE = 1000
NE = 1001
LT = 1002
GE = 1003
GT = 1004
EQ = 1005

atomo_msg = ['Erro Sintático!', 'IDENTIFIER', 'NUM_INT   ', 'NUM_REAL', 'EOS',
             'RELOP', 'ADDOP', 'MULOP', 'IF', 'THEN', 'ELSE', 'BEGIN' , 'END',
             'BOOLEAN' ,'DIV','DO','FALSE','INTEGER','MOD','PROGRAM','READ',
             'TRUE','NOT','VAR','WHILE','WRITE', 'COMMENT', 'PONTO_VIRG', 'VIRGULA', 'PARENTESES', 'SUM', 'SUB', 'MULT', 'PONTO']

reserved_words = {'if': IF, 'then': THEN, 'else': ELSE, 'begin': BEGIN, 'end': END,
                  'boolean': BOOLEAN, 'div': DIV, 'do': DO, 'false': FALSE, 'integer': INTEGER, 
                  'mod': MOD, 'program': PROGRAM, 'read': READ, 'true': TRUE, 'not': NOT, 'var': VAR, 
                  'while': WHILE, 'write': WRITE, 'comment':COMMENT, 'ponto_virg':PONTO_VIRG, 
                  'virgula':VIRGULA, 'parenteses': PARENTESES, 'sum': SUM, 'sub': 'SUB', 'mult': MULT, 'ponto': PONTO}

class Atomo(NamedTuple):
    type: int
    lexeme: str
    value: Union [int, float]
    operator: int               # LE, NE, LT, GE, GT, EQ
    line: int

class LexiconAnalyzer:
    def __init__(self, buffer: str):
        self.line = 1
        self.buffer = buffer + '\0'
        self.i = 0
    
    def next_char(self):
        c = self.buffer[self.i]
        self.i += 1
        return c
    
    def retract(self):
        self.i -= 1

    # analisador lexico
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
            comentario = self.treat_comment(c)
            if comentario:
                return comentario
        if c.isalpha() or c == '_':
            return self.treat_identifier(c)
        elif c.isdigit():
            return self.treat_number(c)
        elif c== ':':
            nextChar=self.next_char()
            if nextChar == '=':
                return Atomo(RELOP,':=', 0, EQ, self.line)
            else:
                self.retract()
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
                self.retract()
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
                self.retract()
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
                self.retract()
                if lexeme.lower() in reserved_words:
                    reserved = reserved_words[lexeme.lower()]
                    return Atomo(reserved, lexeme, 0, 0, self.line)
                else:
                    return Atomo(IDENTIFIER, lexeme, 0, 0, self.line)

    # trata comentarios
    def treat_comment(self, initial: str):
        lexeme = initial
        if initial == '/':  
            nextChar = self.next_char()
            if nextChar == '/':
                lexeme += nextChar
                c = self.next_char()
                while c != '\n' and c != '\0':  
                    lexeme += c
                    c = self.next_char()
                self.line += 1
                return Atomo(ERROR, lexeme, 0, 0, self.line)  
            else:
                self.retract()  
                return None  

        elif initial == '(': 
            nextChar = self.next_char()
            if nextChar == '*':
                lexeme += nextChar
                c = self.next_char()
                while True:
                    if c == '*' and self.next_char() == ')':
                        lexeme += '*)'
                        break
                    lexeme += c
                    if c == '\n':
                        self.line += 1  
                    c = self.next_char()
                return Atomo(COMMENT, lexeme, 0, 0, self.line)  
            else:
                self.retract()  
                return None  

        elif initial == '{':  
            c = self.next_char()
            while c != '}' and c != '\0':  
                lexeme += c
                if c == '\n':
                    self.line += 1  
                c = self.next_char()
            lexeme += '}' 
            return Atomo(ERROR, lexeme, 0, 0, self.line) 

        return None  

    #trata pontuacao
    def treat_punctuation(self, c):
        if c == ';':
            return PONTO_VIRG
        if c == ',':
            return VIRGULA
        if c == '(' or c == ')':
            return PARENTESES
        if c == '.':
            return PONTO

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
        self.current_token = None

    def error(self, message):
        raise Exception(f"Erro sintático na linha {self.current_token.line}: {message}")

    def consume(self, expected_type):
        print(f'Linha: {self.current_token.line} - átomo: {atomo_msg[self.current_token.type]}\t\t lexema: {self.current_token.lexeme}', end='')
        if self.current_token.value != 0:
            print(f'\t\t valor: {self.current_token.value}')
        else:
            print()

        if self.current_token.type == expected_type:
            self.current_token = self.lex.next_atom()
        else:
            self.error(f"Esperado {atomo_msg[expected_type]}, encontrado {atomo_msg[self.current_token.type]}")

    def parse(self):
        self.current_token = self.lex.next_atom()
        self.programa()

    def programa(self):
        self.consume(PROGRAM)
        self.consume(IDENTIFIER)
        if self.current_token.type == PARENTESES and self.current_token.lexeme == '(':
            self.consume(PARENTESES)
            self.lista_de_identificadores()
            self.consume(PARENTESES)
        self.consume(PONTO_VIRG)
        self.bloco()
        self.consume(PONTO)

    def bloco(self):
        if self.current_token.type == VAR:
            self.declaracoes_de_variaveis()
        self.comando_composto()

    def declaracoes_de_variaveis(self):
        self.consume(VAR)
        self.declaracao()
        self.consume(PONTO_VIRG)
        while self.current_token.type == IDENTIFIER:
            self.declaracao()
            self.consume(PONTO_VIRG)

    def declaracao(self):
        self.lista_de_identificadores()
        self.consume(RELOP)  # ':' é um RELOP
        self.tipo()

    def lista_de_identificadores(self):
        self.consume(IDENTIFIER)
        while self.current_token.type == VIRGULA:
            self.consume(VIRGULA)
            self.consume(IDENTIFIER)

    def tipo(self):
        if self.current_token.type == INTEGER:
            self.consume(INTEGER)
        elif self.current_token.type == BOOLEAN:
            self.consume(BOOLEAN)
        else:
            self.error("Tipo inválido")

    def comando_composto(self):
        self.consume(BEGIN)
        self.comando()
        while self.current_token.type == PONTO_VIRG:
            self.consume(PONTO_VIRG)
            self.comando()
        self.consume(END)

    def comando(self):
        if self.current_token.type == IDENTIFIER:
            self.atribuicao()
        elif self.current_token.type == READ:
            self.comando_de_entrada()
        elif self.current_token.type == WRITE:
            self.comando_de_saida()
        elif self.current_token.type == IF:
            self.comando_if()
        elif self.current_token.type == WHILE:
            self.comando_while()
        elif self.current_token.type == BEGIN:
            self.comando_composto()
        else:
            self.error("Comando inválido")

    def atribuicao(self):
        self.consume(IDENTIFIER)
        self.consume(RELOP)  # ':=' é um RELOP
        self.expressao()

    def comando_if(self):
        self.consume(IF)
        self.expressao()
        self.consume(THEN)
        self.comando()
        if self.current_token.type == ELSE:
            self.consume(ELSE)
            self.comando()

    def comando_while(self):
        self.consume(WHILE)
        self.expressao()
        self.consume(DO)
        self.comando()

    def comando_de_entrada(self):
        self.consume(READ)
        self.consume(PARENTESES)
        self.lista_de_identificadores()
        self.consume(PARENTESES)

    def comando_de_saida(self):
        self.consume(WRITE)
        self.consume(PARENTESES)
        self.expressao()
        while self.current_token.type == VIRGULA:
            self.consume(VIRGULA)
            self.expressao()
        self.consume(PARENTESES)

    def expressao(self):
        self.expressao_simples()
        if self.current_token.type == RELOP:
            self.consume(RELOP)
            self.expressao_simples()

    def expressao_simples(self):
        if self.current_token.type in [SUM, SUB]:
            self.consume(self.current_token.type)
        self.termo()
        while self.current_token.type in [SUM, SUB, ADDOP]:
            self.consume(self.current_token.type)
            self.termo()

    def termo(self):
        self.fator()
        while self.current_token.type in [MULT, DIV, MOD]:
            self.consume(self.current_token.type)
            self.fator()

    def fator(self):
        if self.current_token.type == IDENTIFIER:
            self.consume(IDENTIFIER)
        elif self.current_token.type in [NUM_INT, NUM_REAL]:
            self.consume(self.current_token.type)
        elif self.current_token.type == PARENTESES and self.current_token.lexeme == '(':
            self.consume(PARENTESES)
            self.expressao()
            self.consume(PARENTESES)
        elif self.current_token.type == TRUE:
            self.consume(TRUE)
        elif self.current_token.type == FALSE:
            self.consume(FALSE)
        elif self.current_token.type == NOT:
            self.consume(NOT)
            self.fator()
        else:
            self.error("Fator inválido")

# le o arquivo
def read_file():
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        file_name = 'files/input02.pas'

    arq = open(file_name)
    buffer = arq.read()
    arq.close()

    return buffer

def consume(atomo, lex):
    while atomo.type not in [EOS, ERROR]:
        print(f'Linha: {atomo.line} - átomo: {atomo_msg[atomo.type]}\t\t lexema: {atomo.lexeme}', end='')

        if atomo.value != 0:
            print(f'\t\t valor: {atomo.value}')
        else:
            print()
            
        atomo = lex.next_atom()
        
    if atomo.type == ERROR:
        print(f'Linha: {atomo.line} - átomo: {atomo_msg[atomo.type]} Erro na linha {atomo.line}. Caractere inesperado "{lex.buffer[lex.i-1]}"')
    else:
        print(f'Linha: {atomo.line} - átomo: {atomo_msg[atomo.type]}. {atomo.line} linhas analisadas, programa sintaticamente correto.')

def main():
    buffer = read_file()
    lex = LexiconAnalyzer(buffer)
    parser = SyntaxAnalyzer(lex)

    print("Análise Léxica e Sintática:")
    try:
        lex = LexiconAnalyzer(buffer)
        parser.parse()
        print("Análise léxica e sintática concluída com sucesso.")
    except Exception as e:
        print(f"Erro: {str(e)}")
    
    # Verificar se há algum átomo não processado
    final_token = lex.next_atom()
    if final_token.type != EOS:
        print(f"Aviso: Há tokens não processados após o fim do programa na linha {final_token.line}")

main()