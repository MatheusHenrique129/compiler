from typing import NamedTuple
from typing import Union
import sys


ERRO = 0
IDENTIFICADOR = 1
NUM_INT = 2
NUM_REAL = 3
EOS = 4
EOS = 4
RELOP = 5
ADDOP = 6
MULOP = 7

#PALAVRAS RESERVADAS
BEGIN = 8
BOOL = 9
DIV = 10
DO = 11
ELSE = 12
END = 13
FALSE = 14
IF = 15
INT = 16
MOD = 17
PROGRAM = 18
READ = 19
THEN = 20
TRUE = 21
NOT = 22
VAR = 23
WHILE = 24
WRITE = 25

# operador relacional
LE = 1000  # <=
NE = 1001  # !=
LT = 1002  # < 
GE = 1003  # >=
GT = 1004  # >
EQ = 1005  # =

atomo_msg = ['Erro Léxico!', 'IDENTIFICADOR', 'NUM_INT', 'NUM_REAL', 'EOS', 'RELOP', 'ADDOP', 'MULOP   ', 'IF     ', 'THEN     ', 'ELSE   ', 'BEGIN    ' , 'END     ']


palavras_reservadas = {'begin': BEGIN, 'boolean': BOOL, 'div': DIV, 'do': DO, 'else': ELSE, 'end':END, 'false': FALSE, 'if':IF, 
                       'integer': INT, 'mod': MOD, 'program': PROGRAM, 'read': READ, 'then': THEN, 'true': TRUE, 'not': NOT,
                       'var': VAR, 'while': WHILE, 'write': WRITE}

class Atomo(NamedTuple):
    tipo : int
    lexema : str
    valor : Union [int, float]
    operador : int               
    linha : int

class Analisador_Lexico:
    def __init__(self, buffer: str):
        self.linha = 1
        self.buffer = buffer + '\0'
        self.i = 0

    def proximo_char(self):
        c = self.buffer[self.i]
        self.i += 1
        return c
    
    def retrair(self):
        self.i -= 1

    def proximo_atomo(self):
        atomo = Atomo(ERRO, '', 0, 0, self.linha)
        c = self.proximo_char()
        while (c in [' ', '\n', '\t', '\0']):
            if (c == '\n'):
                self.linha += 1
            if (c == '\0'):
                return Atomo(EOS, '', 0, 0, self.linha)
            c = self.proximo_char()
        if c.isalpha() or c == '_':
            return self.tratar_identificador(c)
        elif c.isdigit():
            return self.tratar_numero(c)
        elif c == '<':
            return self.trata_operador_menor(c)
        elif c == '=':
            return Atomo(RELOP, '=', 0, EQ, self.linha)
        return atomo
        ########### TRATAR OS TIPOS DE ATOMOS...

    def trata_operador_menor(self, c: str):
        c = self.proximo_char()
        estado = 1
        while True:
            if estado == 1:
                if c == '=':
                    estado = 2
                elif c == '>':
                    estado = 3
                else:
                    estado = 4
            elif estado == 2:
                return Atomo(RELOP, '<=', 0, LE, self.linha)
            elif estado == 3:
                return Atomo(RELOP, '<>', 0, NE, self.linha)
            elif estado == 4:
                self.retrair()
                return Atomo(RELOP, '<', 0, LT, self.linha)


    def tratar_numero(self, c: str):
        lexema = c
        c = self.proximo_char()
        estado = 1
        while True:
            if estado == 1:
                if c.isdigit():
                    lexema += c
                    estado = 1
                    c = self.proximo_char()
                elif c == '.':
                    lexema += c
                    estado = 3
                    c = self.proximo_char()
                else:
                    estado = 2
            elif estado == 2:
                self.retrair()
                return Atomo(NUM_INT, lexema, int(lexema), 0, self.linha)
            elif estado == 3:
                if c.isdigit():
                    lexema += c
                    estado = 4
                    c = self.proximo_char()
                else:
                    return Atomo(ERRO, '', 0, 0, self.linha)
            elif estado == 4:
                if c.isdigit():
                    lexema += c
                    estado = 4
                    c = self.proximo_char()
                else:
                    estado = 5
            elif estado == 5:
                self.retrair()
                valor = float(lexema)
                return Atomo(NUM_REAL, lexema, valor, 0, self.linha)
            
    def tratar_identificador(self, c: str):
        lexema = c
        c = self.proximo_char()
        estado = 1
        while True:
            if estado == 1:
                if c.isdigit() or c.isalpha() or c == '_':
                    lexema += c
                    estado = 1
                    c = self.proximo_char()
                else:
                    estado = 2
            elif estado == 2:
                self.retrair()
                if lexema.lower() in palavras_reservadas:
                    reservada = palavras_reservadas[lexema.lower()]
                    return Atomo(reservada, lexema, 0, 0, self.linha)
                else:
                    return Atomo(IDENTIFICADOR, lexema, 0, 0, self.linha)
                
def leia_arquivo():
    if len(sys.argv) > 1:
        nome_arquivo = sys.argv[1]
    else:
        nome_arquivo = 'teste.txt'


def main():
    buffer = leia_arquivo()
    lex = Analisador_Lexico(buffer)
    atomo = lex.proximo_atomo()
    while (atomo.tipo != EOS and atomo.tipo != ERRO):
        print(f'Linha: {atomo.linha}', end='')
        print(f' - átomo: {atomo_msg[atomo.tipo]}', end='')
        print(f'\t\t lexema: {atomo.lexema}', end='')
        print(f'\t\t valor: {atomo.valor}')
        atomo = lex.proximo_atomo()

    print(f'Linha: {atomo.linha}', end='')
    print(f' - átomo: {atomo_msg[atomo.tipo]}', end='')

main()