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
             'TRUE','NOT','VAR','WHILE','WRITE', 'COMMENT', 'PONTO_VIRG', 'VIRGULA', 'PARENTESES', 'SUM', 'SUB', 'MULT']

reserved_words = {'if': IF, 'then': THEN, 'else': ELSE, 'begin': BEGIN, 'end': END,
                  'boolean': BOOLEAN, 'div': DIV, 'do': DO, 'false': FALSE, 'integer': INTEGER, 
                  'mod': MOD, 'program': PROGRAM, 'read': READ, 'true': TRUE, 'not': NOT, 'var': VAR, 
                  'while': WHILE, 'write': WRITE, 'comment':COMMENT, 'ponto_virg':PONTO_VIRG, 
                  'virgula':VIRGULA, 'parenteses': PARENTESES, 'sum': SUM, 'sub': 'SUB', 'mult': MULT}

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
        elif c == ':':
            return Atomo(RELOP, ':', 0, EQ, self.line)
        elif c == ';':
            return Atomo(PONTO_VIRG, ';', 0, 0, self.line)
        elif c == ',':
            return Atomo(VIRGULA, ',', 0, 0, self.line)
        elif c == '(':
            return Atomo(PARENTESES, '(', 0, 0, self.line)
        elif c == ')':
            return Atomo(PARENTESES, ')', 0, 0, self.line)
        elif c == '+':
            return Atomo(SUM, '+', 0, 0, self.line)
        elif c == '*':
            return Atomo(MULT, '*', 0, 0, self.line)
        elif c == '/':
            return Atomo(DIV, '/', 0, 0, self.line)
        elif c == '-':
            return Atomo(SUB, '-', 0, 0, self.line)
        return atomo

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
     
def read_file():
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        file_name = 'case_success.pas'

    arq = open(file_name)
    buffer = arq.read()
    arq.close()

    return buffer

def main():
    buffer = read_file()
    lex = LexiconAnalyzer(buffer)
    atomo = lex.next_atom()

    while (atomo.type != EOS and atomo.type != ERROR):
        print(f'Linha: {atomo.line}', end='')
        print(f' - átomo: {atomo_msg[atomo.type]}', end='')
        print(f'\t\t lexema: {atomo.lexeme}', end='')

        if atomo.value != 0:
            print(f'\t\t valor: {atomo.value}')
        else:
            print(f'\t\t')
            
        atomo = lex.next_atom()
        
    
    if atomo.type == ERROR:
        print(f' - átomo: {atomo_msg[atomo.type]} Erro léxico na linha {atomo.line}: Caractere inesperado ({atomo.lexeme})')
    else:
        print(f'Linha: {atomo.line}', end='')
        print(f' - átomo: {atomo_msg[atomo.type]}', end='')

main()