from atomo import Atomo
from constants import *

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
        elif c == '.':
            return Atomo(PONTO, '.', 0, 0, self.line)
        
        print(f"Análise Léxica: Linha {atomo.line} - Átomo: {atomo_msg[atomo.type]}, Lexema: {atomo.lexeme}")
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
    
    def lexicon(atomo, lex):
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
            print(f'Linha: {atomo.line} - átomo: {atomo_msg[atomo.type]}. {atomo.line} linhas analisadas, programa lexicamente correto.')
