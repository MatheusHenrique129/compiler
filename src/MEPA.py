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
                return Atomo(RELOP, '>=', 0, GE, self.line)
            elif state == 4:
                return Atomo(RELOP, '<>', 0, NE, self.line)
            elif state == 5:
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
        self.semantic = SemanticAnalyzer()  # Inicializa o analisador semântico
        self.var_addresses = {}

    def error(self, message):
        raise Exception(f"Erro sintático na linha {self.lookahead.line}: {message}")

    def consume(self, expected_type):
        self.handle_comment() # valida se tem um Comentário antes de consumir o atomo
        #print(f'Linha: {self.lookahead.line} - átomo: {atomo_msg[self.lookahead.type]}\t\t lexema: {self.lookahead.lexeme}', end='')
        #if self.lookahead.value != 0:
        #    print(f'\t\t valor: {self.lookahead.value}')
        #else:
        #    print()
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
        self.semantic.start_program()  # Código inicial do programa
        self.consume(PROGRAM)
        self.consume(IDENTIFIER)
        if self.lookahead.type == PARENTHESIS and self.lookahead.lexeme == '()':
            self.consume(PARENTHESIS)
            self.list_identifiers()
            self.consume(PARENTHESIS)
        self.consume(PONTO_VIRG)
        self.block()
        self.consume(DOT)
        self.semantic.end_program()  # Código final do programa
        self.semantic.print_output()

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
        var_list = []
        while self.lookahead.type == IDENTIFIER:
            var_name = self.lookahead.lexeme
            self.consume(IDENTIFIER)
            var_list.append(var_name)
            if self.lookahead.type == VIRGULA:
                self.consume(VIRGULA)
        self.consume(RELOP)  # Consome o ":"
        self.type_declaration()
        for var_name in var_list:
            self.var_addresses[var_name] = self.semantic.memory_index
            self.semantic.memory_index += 1
        self.semantic.add_memory(len(var_list))

    def list_identifiers(self):
        """Carrega variáveis de entrada"""
        while self.lookahead.type == IDENTIFIER:
            var_name = self.lookahead.lexeme
            if var_name in self.var_addresses:
                var_address = self.var_addresses[var_name]
                self.semantic.assign(var_address)  # Esta função deve atualizar corretamente o valor da variável
            else:
                self.error(f"Variável '{var_name}' não declarada")
            self.consume(IDENTIFIER)
            if self.lookahead.type == VIRGULA:
                self.consume(VIRGULA)

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
            self.semantic.write()
        elif self.lookahead.type == IF:
            self.command_if()
        elif self.lookahead.type == WHILE:
            self.command_while()
        elif self.lookahead.type == BEGIN:
            self.compound_command()
        else:
            self.error("Comando inválido")

    def assignment(self):
        var_name = self.lookahead.lexeme
        if var_name not in self.var_addresses:
            self.error(f"Variável '{var_name}' não declarada")

        self.consume(IDENTIFIER)
        self.consume(RELOP)  # Consome ":="
        self.expression()
        self.semantic.assign(self.var_addresses[var_name])

    def command_if(self):
        self.consume(IF)  # Consome 'if'
        condition_code = self.expression()  # Código para a condição
        self.consume(THEN)  # Consome 'then'
        self.command()
        # Executa o bloco verdadeiro
        true_block = lambda: self.command()
        # Verifica se há um bloco 'else'
        false_block = None
        if self.lookahead.type == ELSE:
            self.consume(ELSE)
            self.command()
            false_block = lambda: self.command()  # Executa o bloco falso
        # Chamada semântica
        # self.semantic.generate_if(condition_code, true_block, false_block)

    def command_while(self):
        start_label = self.semantic.new_label()  # início do loop
        end_label = self.semantic.new_label()    # fim do loop
        self.consume(WHILE)

        self.semantic.add_label(start_label)  # início no código
        # Gera o código para a condição do loop
        self.expression()
        self.semantic.jump_if_false(end_label)  # Salta para o final se a condição for falsa

        self.consume(DO)
        self.command()

        self.semantic.jump(start_label)  # Salta de volta ao início para reavaliar a condição
        self.semantic.add_label(end_label)  # Coloca o rótulo de fim do loop

    def input_command(self):
        self.semantic.generate_code("LEIT")
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
            op_type = self.lookahead.operator
            self.consume(RELOP)
            self.simple_expression()
            # Gera instruções de comparação baseadas no operador
            if op_type == LE:
                self.semantic.compare_less_equal() # Semântico
            elif op_type == NE:
                self.semantic.compare_not_equal() # Semântico
            elif op_type == LT:
                self.semantic.compare_less() # Semântico
            elif op_type == GE: 
                self.semantic.compare_greater_equal()   # Semântico
            elif op_type == GT:
                self.semantic.compare_greater() # Semântico
            elif op_type == EQ:
                self.semantic.compare_equal() # Semântico

    def simple_expression(self):
        if self.lookahead.type in [SUM, SUB]:
            if self.lookahead.type == SUM:
                self.consume(SUM)
                self.semantic.add_op() # Semântico
            if self.lookahead.type == SUB:
                self.consume(SUB)
                self.semantic.sub_op() # Semântico
        self.term()
        while self.lookahead.type in {SUM, SUB, ADDOP}:
            if self.lookahead.type == SUM:
                self.consume(SUM)
                self.term()
                self.semantic.add_op() # Semântico
            elif self.lookahead.type == SUB:
                self.consume(SUB)
                self.term()
                self.semantic.sub_op() # Semântico
            else:
                self.consume(self.lookahead.type)
                self.term()

    def term(self):
        self.factor()
        while self.lookahead.type in {MULT, DIV, MOD}:
            if self.lookahead.type == MULT:
                self.consume(MULT)
                self.factor()
                self.semantic.mul_op() # Semântico
            if self.lookahead.type == DIV:
                self.consume(DIV)
                self.factor()
                self.semantic.div_op() # Semântico
            if self.lookahead.type == MOD:
                self.consume(MOD)
                self.factor()
                self.semantic.mod_op() # Semântico

    def factor(self):
        if self.lookahead.type == IDENTIFIER:
            var_name = self.lookahead.lexeme
            if var_name in self.var_addresses:
                var_address = self.var_addresses[var_name]
                self.semantic.load_var(var_address)
            else:
                self.error(f"Variável '{var_name}' não declarada")
            self.consume(IDENTIFIER)
        elif self.lookahead.type in [NUM_INT, NUM_REAL]:
            value = self.lookahead.value
            self.semantic.load_const(value)
            self.consume(self.lookahead.type)
        elif self.lookahead.type == PARENTHESIS and self.lookahead.lexeme == '(':
            self.consume(PARENTHESIS)
            self.expression()
            self.consume(PARENTHESIS)
        elif self.lookahead.type in [TRUE, FALSE]:
            self.handle_boolean()
        elif self.lookahead.type == NOT:
            self.consume(NOT)
            self.factor()
        else:
            self.error("Fator inválido")

    def handle_boolean(self):
        if self.lookahead.type == TRUE:
            self.semantic.load_const(1)
            self.consume(TRUE)
        elif self.lookahead.type == FALSE:
            self.semantic.load_const(0)
            self.consume(FALSE)

class SemanticAnalyzer:
    def __init__(self):
        self.output = []
        self.memory_index = 0
        self.label_count = 1

    def new_label(self):
        label = f"L{self.label_count}"
        self.label_count += 1
        return label

    def generate_code(self, code):
        self.output.append(code)

    def add_memory(self, count):
        #Aloca memória para variáveis
        self.generate_code(f"AMEM {count}")
        self.memory_index += count

    def release_memory(self, count):
        #Libera memória
        self.generate_code(f"DMEM {count}")
        self.memory_index -= count

    def start_program(self):
        #Inicia o programa
        self.generate_code("INPP")

    def end_program(self):
        #Finaliza o programa
        self.generate_code("PARA")

    def assign(self, var_address):
        #Armazena o valor no endereço de variável
        self.generate_code(f"ARMZ {var_address}")

    def load_const(self, value):
        #Carrega uma constante para o topo da pilha
        self.generate_code(f"CRCT {value}")

    def load_var(self, var_address):
        #Carrega o valor de uma variável para o topo da pilh
        self.generate_code(f"CRVL {var_address}")

    def add_op(self):
        # Operação de adição
        self.generate_code("SOMA")

    def mod_op(self):
        # Operação de módulo
        self.generate_code("MOD")

    def sub_op(self):
        #Operação de subtração
        self.generate_code("SUBT")

    def mul_op(self):
        # Operação de multiplicação
        self.generate_code("MULT")

    def div_op(self):
        #Operação de divisão
        self.generate_code("DIVI")

    def compare_equal(self):
        # Comparação de igualdade
        self.generate_code("CMIG")

    def compare_less(self):
        # Comparação de menor
        self.generate_code("CMME")

    def compare_not_equal(self):
        # Comparação de diferente
        self.generate_code("CMDG")

    def compare_greater_equal(self):
        # Comparação de maior igual
        self.generate_code("CMAG")

    def compare_less_equal(self):
        #Comparação de menor igual
        self.generate_code("CMEG")

    def compare_greater(self):
        #Comparação de maior
        self.generate_code("CMMA")

    def jump_if_false(self, label):
        # Desvia se a condição for falsa
        self.generate_code(f"DSVF {label}")

    def jump(self, label):
        # Desvio incondicional"""
        self.generate_code(f"DSVS {label}")

    def add_label(self, label):
        # desvio
        self.generate_code(f"{label}: NADA")

    def write(self):
        # Função write
        self.generate_code("IMPR")

    def print_output(self):
        #Output no terminal
        #print("\n******************** MEPA ********************\n")
        #for line in self.output:
        print()

    # controle de fluxo

    def generate_if(self, condition_code, true_block, false_block=None):
        # estrutura if-else
        label_false = self.new_label()
        label_end = self.new_label()

        # Código para condição
        self.generate_code(condition_code)
        self.jump_if_false(label_false)

        # Bloco verdadeiro
        true_block()

        # Desvio para o fim do if, se houver bloco falso
        if false_block:
            self.jump(label_end)

        # Rótulo para o bloco falso
        self.add_label(label_false)
        if false_block:
            false_block()

        # Rótulo final
        if false_block:
            self.add_label(label_end)

    def generate_while(self, condition_code, loop_block):
        # estrutura while
        label_start = self.new_label()
        label_end = self.new_label()

        # Rótulo de início do loop
        self.add_label(label_start)

        # Condição de continuidade do loop
        self.generate_code(condition_code)  # CRVL é chamados aqui
        self.jump_if_false(label_end)

        # Bloco de repetição
        loop_block()

        # início do loop
        self.jump(label_start)

        # fim do loop
        self.add_label(label_end)

class MEPAInterpreter:
    def __init__(self):
        self.pilha = []   # Pilha para execução
        self.memoria = {} # Memória simulada
        self.codigo = []  # Código MEPA carregado
        self.ip = 0       # Instruction pointer
        self.arquivo_atual = None  # Nome do arquivo carregado
        self.codigo_modificado = False 
        
    def carregar_codigo(self, codigo,arquivo=None):
        self.codigo = [linha.strip() for linha in codigo if linha.strip()]  # Remove espaços e linhas vazias
        self.arquivo_atual = arquivo
        self.codigo_modificado = False  # Reseta o status de modificação
        print(f"Código carregado com sucesso de '{arquivo}'." if arquivo else "Código carregado com sucesso.")

    def salvar_codigo(self):
        if not self.arquivo_atual:
            print("Nenhum arquivo associado. Use LOAD para carregar ou informe o nome ao salvar.")
            return False
        try:
            with open(self.arquivo_atual, 'w') as f:
                f.write("\n".join(self.codigo))
            self.codigo_modificado = False
            print(f"Código salvo com sucesso em '{self.arquivo_atual}'.")
            return True
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {e}")
            return False
        
##INSTRUÇÕES MEPA
    def executar(self):
        while self.ip < len(self.codigo):
            instrucao = self.codigo[self.ip]
            self.ip += 1
            if instrucao.startswith("INPP"):
                # Inicia o programa principal
                self.pilha = []  # Limpa a pilha
                self.memoria = {}  # Limpa a memória
                print("Programa iniciado (INPP).")

            elif instrucao.startswith("AMEM"):
                _, m = instrucao.split()
                # Aloca memória
                for i in range(int(m)):
                    self.memoria[len(self.memoria)] = 0  # Inicializa posições com 0
                print(f"Memória alocada: {m} posições.")

            elif instrucao.startswith("DMEM"):
                _, m = instrucao.split()
                # Desaloca memória
                for i in range(int(m)):
                    if len(self.memoria) > 0:
                        self.memoria.pop(len(self.memoria) - 1)
                print(f"Memória desalocada: {m} posições.")

            elif instrucao.startswith("PARA"):
                print("Programa finalizado (PARA).")
                break

            elif instrucao.startswith("CRCT"):
                _, valor = instrucao.split()
                self.pilha.append(int(valor))

            elif instrucao.startswith("CRVL"):
                _, endereco = instrucao.split()
                self.pilha.append(self.memoria[int(endereco)])

            elif instrucao.startswith("SOMA"):
                b = self.pilha.pop()
                a = self.pilha.pop()
                self.pilha.append(a + b)

            elif instrucao.startswith("SUBT"):
                b = self.pilha.pop()
                a = self.pilha.pop()
                self.pilha.append(a - b)

            elif instrucao.startswith("MULT"):
                b = self.pilha.pop()
                a = self.pilha.pop()
                self.pilha.append(a * b)

            elif instrucao.startswith("DIVI"):
                b = self.pilha.pop()
                a = self.pilha.pop()
                if b == 0:
                    raise Exception("Erro: Divisão por zero.")
                self.pilha.append(a // b)
                
            elif instrucao.startswith("INVR"):
                a = self.pilha.pop()
                self.pilha.append(-a)

            elif instrucao.startswith("ARMZ"):
                _, endereco = instrucao.split()
                self.memoria[int(endereco)] = self.pilha.pop()

            elif instrucao.startswith("CONJ"):
                b = self.pilha.pop()
                a = self.pilha.pop()
                self.pilha.append(a and b)

            elif instrucao.startswith("DISJ"):
                b = self.pilha.pop()
                a = self.pilha.pop()
                self.pilha.append(a or b)
            elif instrucao.startswith("CMME"):
                b = self.pilha.pop()
                a = self.pilha.pop()
                self.pilha.append(1 if a < b else 0)

            elif instrucao.startswith("CMMA"):
                b = self.pilha.pop()
                a = self.pilha.pop()
                self.pilha.append(1 if a > b else 0)

            elif instrucao.startswith("CMIG"):
                b = self.pilha.pop()
                a = self.pilha.pop()
                self.pilha.append(1 if a == b else 0)

            elif instrucao.startswith("CMDG"):
                b = self.pilha.pop()
                a = self.pilha.pop()
                self.pilha.append(1 if a != b else 0)

            elif instrucao.startswith("CMEG"):
                b = self.pilha.pop()
                a = self.pilha.pop()
                self.pilha.append(1 if a <= b else 0)

            elif instrucao.startswith("CMAG"):
                b = self.pilha.pop()
                a = self.pilha.pop()
                self.pilha.append(1 if a >= b else 0)

            elif instrucao.startswith("DSVS"):
                _, endereco = instrucao.split()
                self.ip = int(endereco) - 1 # Desvio incondicional (subtraímos 1 para alinhar com a lista de código)

            elif instrucao.startswith("DSVF"):
                _, endereco = instrucao.split()
                condicao = self.pilha.pop()
                if condicao == 0:
                    self.ip = int(endereco) - 1  # Desvio se falso

            elif instrucao.startswith("NADA"):
                pass

            elif instrucao.startswith("IMPR"):
                valor = self.pilha.pop()
                print(f"IMPR: {valor}")
            else:
                raise Exception(f"Instrução inválida: {instrucao}")
        print("Execução concluída. Pilha final:", self.pilha)

    def repl(self):
        while True:
            comando = input("> ").strip().upper()

            if comando.startswith("LOAD"):
                if self.codigo_modificado:
                    salvar = input("Há modificações não salvas. Deseja salvar? (S/N): ").strip().upper()
                    if salvar == "S":
                        if not self.salvar_codigo():
                            continue
                try:
                    partes = comando.split(maxsplit=1)
                    if len(partes) < 2:
                        print("Erro: O comando LOAD requer o nome do arquivo. Exemplo: LOAD exemplo.mepa")
                        continue
                    arquivo = partes[1]
                    with open(arquivo, 'r') as f:
                        codigo = f.readlines()
                        self.carregar_codigo(codigo, arquivo=arquivo)
                except FileNotFoundError:
                    print(f"Erro: Arquivo '{arquivo}' não encontrado.")
                except Exception as e:
                    print(f"Erro ao carregar o arquivo: {e}")

            elif comando == "LIST": 
                if not self.codigo:
                    print("Nenhum código carregado.")
                else:
                    print("\n--- Código Carregado ---")
                    for i, linha in enumerate(self.codigo):
                        print(f"{i + 1}: {linha.strip()}")

            elif comando == "RUN":  
                if self.codigo:
                    print("\n--- Iniciando Execução ---")
                    self.executar()
                else:
                    print("Nenhum código carregado. Use o comando LOAD primeiro.")

            elif comando == "SAVE":
                if not self.salvar_codigo():
                    novo_arquivo = input("Informe o nome do arquivo para salvar: ").strip()
                    try:
                        with open(novo_arquivo, 'w') as f:
                            f.write("\n".join(self.codigo))
                        self.codigo_modificado = False
                        print(f"Código salvo com sucesso em '{novo_arquivo}'.")
                    except Exception as e:
                        print(f"Erro ao salvar o arquivo: {e}")

            elif comando == "EXIT":
                if self.codigo_modificado:
                    salvar = input("Há modificações não salvas. Deseja salvar? (S/N): ").strip().upper()
                    if salvar == "S":
                        if not self.salvar_codigo():
                            continue
                print("Encerrando o programa.")
                break

            else:
                print("Comando inválido.")
    
    

    # def deletar_linha(self, linha):
    #     if linha < 1 or linha > len(self.codigo):
    #         print(f"Linha {linha} inexistente.")
    #     else:
    #         self.codigo.pop(linha - 1)
    #         print(f"Linha {linha} removida.")


# le o arquivo
# def read_file():
#     if len(sys.argv) > 1:
#         file_name = sys.argv[1]
#     else:
#         file_name = r"C:\Users\gugsr\OneDrive\Documents\GitHub\compiler\src\files\success_case.pas"

#     arq = open(file_name)
#     buffer = arq.read()
#     arq.close()

#     return buffer

# def main():
#     buffer = read_file()  # Lê o arquivo de entrada
#     lex = LexiconAnalyzer(buffer)  # Inicializa o analisador léxico
#     synthetic = SyntaxAnalyzer(lex)  # Inicializa o analisador sintático

#     try:
#         # Etapa de análise léxica e sintática
#         synthetic.synthetic()  
#         print(f"{synthetic.lex.line} linhas analisadas, análise léxica e sintática concluída com sucesso.")
        
#         # Recupera o código gerado pelo analisador semântico
#         codigo_mepa = synthetic.semantic.output
        
#         # Inicializa o interpretador
#         interpreter = MEPAInterpreter()
#         interpreter.carregar_codigo(codigo_mepa)  # Carrega o código no interpretador
        
#         # Mostra o código gerado
#         print("\n--- Código MEPA Gerado ---")
#         for linha in interpreter.codigo:
#             print(linha)
        
#         # Executa o código
#         print("\n--- Iniciando Execução ---")
#         interpreter.executar()

#     except Exception as e:
#         print(f"Erro: {str(e)}")

    
    
#main()

if __name__ == "__main__":
        interpreter = MEPAInterpreter()
        interpreter.repl()


#AJUSTAR PRINTAR 20 POR VEZ
#ERRO NO COMANDO RUN IndexError: pop from empty list
#IMPLEMENTAR INS, DEL,DEBUG(STACK, STOP)