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

    def __init__(self, lexicon_analyzer):
        self.lex = lexicon_analyzer
        self.current_atom = self.lex.next_atom()

    def next(self):
        """Avança para o próximo átomo."""
        self.current_atom = self.lex.next_atom()

    def expect(self, atom_type, error_message):
        """Verifica se o átomo atual é do tipo esperado e avança."""
        if self.current_atom.type == atom_type:
            self.next()
        else:
            self.error(error_message)

    def error(self, message):
        """Levanta um erro de sintaxe."""
        raise SyntaxError(f"Erro na linha {self.current_atom.line}: {message}")

    # Funções de análise para cada regra da gramática

    def analyze_program(self):
        """<programa> ::= program identificador [( <lista de identificadores> )] ; <bloco>."""
        self.expect(PROGRAM, "Esperado 'program' no início.")
        self.expect(IDENTIFIER, "Esperado identificador após 'program'.")
        if self.current_atom.type == PARENTESES:  # Se houver uma lista de identificadores entre parênteses
            self.analyze_identifier_list()
        self.expect(PONTO_VIRG, "Esperado ';' após a declaração do programa.")
        self.analyze_block()

    def analyze_block(self):
        """<bloco> ::= [<declarações de variáveis>] <comando composto>."""
        if self.current_atom.type == VAR:
            self.analyze_variable_declarations()
        self.analyze_compound_command()

    def analyze_variable_declarations(self):
        """<declarações de variáveis> ::= var <declaração> {; <declaração> };"""
        self.expect(VAR, "Esperado 'var' para declaração de variáveis.")
        self.analyze_declaration()
        while self.current_atom.type == PONTO_VIRG:
            self.next()
            self.analyze_declaration()

    def analyze_declaration(self):
        """<declaração> ::= <lista de identificadores> : <tipo>."""
        self.analyze_identifier_list()
        self.expect(RELOP, "Esperado ':' após lista de identificadores.")
        self.analyze_type()

    def analyze_identifier_list(self):
        """<lista de identificadores> ::= identificador { , identificador }"""
        self.expect(IDENTIFIER, "Esperado identificador.")
        while self.current_atom.type == VIRGULA:
            self.next()
            self.expect(IDENTIFIER, "Esperado identificador após ','.")
    
    def analyze_type(self):
        """<tipo> ::= integer | boolean."""
        if self.current_atom.type in [INTEGER, BOOLEAN]:
            self.next()
        else:
            self.error("Esperado 'integer' ou 'boolean' para tipo de variável.")

    def analyze_compound_command(self):
        """<comando composto> ::= begin <comando> { ; <comando> } end."""
        self.expect(BEGIN, "Esperado 'begin' no início do comando composto.")
        self.analyze_command()
        while self.current_atom.type == PONTO_VIRG:
            self.next()
            self.analyze_command()
        self.expect(END, "Esperado 'end' no final do comando composto.")

    def analyze_command(self):
        """<comando> ::= <atribuição> | <comando de entrada> | <comando de saída> | <comando if> | <comando while> | <comando composto>."""
        if self.current_atom.type == IDENTIFIER:
            self.analyze_assignment()
        elif self.current_atom.type == READ:
            self.analyze_input_command()
        elif self.current_atom.type == WRITE:
            self.analyze_output_command()
        elif self.current_atom.type == IF:
            self.analyze_if_command()
        elif self.current_atom.type == WHILE:
            self.analyze_while_command()
        elif self.current_atom.type == BEGIN:
            self.analyze_compound_command()
        else:
            self.error("Comando desconhecido ou inesperado.")

    def analyze_assignment(self):
        """<atribuição> ::= identificador := <expressao> ;"""
        self.expect(IDENTIFIER, "Esperado identificador na atribuição.")
        self.expect(RELOP, "Esperado ':=' após identificador.")
        self.analyze_expression()
        self.expect(PONTO_VIRG, "Esperado ';' no final da atribuição.")

    def analyze_input_command(self):
        """<comando de entrada> ::= read ( <lista de identificadores> )"""
        self.expect(READ, "Esperado 'read'.")
        self.expect(PARENTESES, "Esperado '(' após 'read'.")
        self.analyze_identifier_list()
        self.expect(PARENTESES, "Esperado ')' no comando de leitura.")

    def analyze_output_command(self):
        """<comando de saida> ::= write ( <expressao> { , <expressao> } )"""
        self.expect(WRITE, "Esperado 'write'.")
        self.expect(PARENTESES, "Esperado '(' após 'write'.")
        self.analyze_expression()
        while self.current_atom.type == VIRGULA:
            self.next()
            self.analyze_expression()
        self.expect(PARENTESES, "Esperado ')' no comando de saída.")

    def analyze_if_command(self):
        """<comando if> ::= if <expressao> then <comando> [else <comando>]"""
        self.expect(IF, "Esperado 'if'.")
        self.analyze_expression()
        self.expect(THEN, "Esperado 'then'.")
        self.analyze_command()
        if self.current_atom.type == ELSE:
            self.next()
            self.analyze_command()

    def analyze_while_command(self):
        """<comando while> ::= while <expressao> do <comando>"""
        self.expect(WHILE, "Esperado 'while'.")
        self.analyze_expression()
        self.expect(DO, "Esperado 'do'.")
        self.analyze_command()

    def analyze_expression(self):
        """<expressao> ::= <expressao simples> [<operador relacional> <expressao simples>]"""
        self.analyze_simple_expression()
        if self.current_atom.type == RELOP:
            self.next()
            self.analyze_simple_expression()

    def analyze_simple_expression(self):
        """<expressao simples> ::= [+ | −] <termo> { <operador de adição> <termo> }"""
        if self.current_atom.type in [SUM, SUB]:
            self.next()
        self.analyze_term()
        while self.current_atom.type == ADDOP:
            self.next()
            self.analyze_term()

    def analyze_term(self):
        """<termo> ::= <fator> { <operador de multiplicação> <fator> }"""
        self.analyze_factor()
        while self.current_atom.type == MULOP:
            self.next()
            self.analyze_factor()

    def analyze_factor(self):
        """<fator> ::= identificador | numero | ( <expressao> ) | true | false | not <fator>"""
        if self.current_atom.type == IDENTIFIER:
            self.next()
        elif self.current_atom.type == NUM_INT:
            self.next()
        elif self.current_atom.type == PARENTESES and self.current_atom.lexeme == '(':
            self.next()
            self.analyze_expression()
            self.expect(PARENTESES, "Esperado ')' após expressão.")
        elif self.current_atom.type == TRUE or self.current_atom.type == FALSE:
            self.next()
        elif self.current_atom.type == NOT:
            self.next()
            self.analyze_factor()
        else:
            self.error("Esperado identificador, número, true, false ou expressão entre parênteses.")



def read_file():
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        file_name = r'C:\Users\gugsr\OneDrive\Documents\GitHub\compiler\src\input02.pas'

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
        print(f'Linha: {atomo.line} - átomo: {atomo_msg[atomo.type]}. {atomo.line} linhas analisadas, programa lexicamente correto.')

def main():
    buffer = read_file()  # Função que lê o arquivo de entrada
    lex = LexiconAnalyzer(buffer)
    sintax_analyzer = SintaxAnalyzer(lex)
    atomo=lex.next_atom()

    consume(atomo, lex)
    try:
        sintax_analyzer.analyze_program()  # Começa pela regra do programa
        print("Programa sintaticamente correto.")
    except SyntaxError as e:
        print(e)
   

main()