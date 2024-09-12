from typing import NamedTuple
from typing import Union
import sys

ERRO = 0
IDENTIFICADOR = 1
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
NOT= 21
VAR= 22
WHILE= 23
WRITE= 24

# operador relacional
LE = 1000
NE = 1001
LT = 1002
GE = 1003
GT = 1004
EQ = 1005


atomo_msg = ['Erro Léxico!', 'IDENTIFICADOR', 'NUM_INT   ', 'NUM_REAL', 'EOS',
             'RELOP', 'ADDOP', 'MULOP', 'IF', 'THEN', 'ELSE   ', 'BEGIN    ' , 'END     ']

palavras_reservadas = {'if': IF, 'then': THEN, 'else': ELSE, 'begin': BEGIN, 'end': END,
                    'boolean': BOOLEAN, 'div': DIV, 'do': DO, 'false': FALSE, 'integer': INTEGER, 
                    'mod': MOD, 'program': PROGRAM, 'read': READ, 'true': TRUE, 'not': NOT, 'var': VAR, 
                    'while': WHILE, 'write': WRITE}

class Atomo(NamedTuple):
    tipo : int
    lexema : str
    valor : Union [int, float]
    operador : int               # LE, NE, LT, GE, GT, EQ
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
        while (c in [' ', '\n', '\t', '\r', '\0']):
            if (c == '\n'):
                self.linha += 1
            if (c == '\0'):
                return Atomo(EOS, '', 0, 0, self.linha)
            c = self.proximo_char()
        if c in ['/', '(', '{']:  
            comentario = self.tratar_comentario(c)
            if comentario:
                return comentario
        if c.isalpha() or c == '_':
            return self.tratar_identificador(c)
        elif c.isdigit():
            return self.tratar_numero(c)
        elif c == '<':
            return self.trata_operador_menor(c)
        elif c == ':':
            return Atomo(RELOP, ':', 0, EQ, self.linha)
        return atomo

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
                else:
                    estado = 2
            elif estado == 2:
                self.retrair()
                return Atomo(NUM_INT, lexema, int(lexema), 0, self.linha)

    def tratar_identificador(self, c: str):
        lexema = c
        c = self.proximo_char()
        estado = 1
        while True:
            if estado == 1:
                if c.isdigit() or c.isalpha() or c == '_':
                    lexema += c
                    if len(lexema) > 20:
                        return Atomo(ERRO, lexema, 0, 0, self.linha)
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
                
    def tratar_comentario(self, inicial: str):
        lexema = inicial
        if inicial == '/':  
            proximo = self.proximo_char()
            if proximo == '/':
                lexema += proximo
                c = self.proximo_char()
                while c != '\n' and c != '\0':  
                    lexema += c
                    c = self.proximo_char()
                self.linha += 1
                return Atomo(ERRO, lexema, 0, 0, self.linha)  
            else:
                self.retrair()  
                return None  

        elif inicial == '(': 
            proximo = self.proximo_char()
            if proximo == '*':
                lexema += proximo
                c = self.proximo_char()
                while True:
                    if c == '*' and self.proximo_char() == ')':
                        lexema += '*)'
                        break
                    lexema += c
                    if c == '\n':
                        self.linha += 1  
                    c = self.proximo_char()
                return Atomo(ERRO, lexema, 0, 0, self.linha)  
            else:
                self.retrair()  
                return None  

        elif inicial == '{':  
            c = self.proximo_char()
            while c != '}' and c != '\0':  
                lexema += c
                if c == '\n':
                    self.linha += 1  
                c = self.proximo_char()
            lexema += '}' 
            return Atomo(ERRO, lexema, 0, 0, self.linha) 

        return None  

        
def leia_arquivo():
    if len(sys.argv) > 1:
        nome_arquivo = sys.argv[1]
    else:
        nome_arquivo = 'teste2.txt'

    arq = open(nome_arquivo)
    buffer = arq.read()
    arq.close()

    return buffer

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