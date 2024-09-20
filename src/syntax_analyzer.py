from constants import *

class SyntaxAnalyzer:
    def __init__(self, lexicon_analyzer):
        self.lex = lexicon_analyzer
        self.lookahead = None

    def error(self, message):
        raise Exception(f"Erro sintático na linha {self.lookahead.line}: {message}")

    def print_syntax_status(rule_name, token):
        print(f"Análise Sintática: Regra '{rule_name}' - Token atual: {atomo_msg[token.type]}")

    def consume(self, expected_type):
        if self.lookahead.type == expected_type:
            self.lookahead = self.lex.next_atom()
        else:
            self.error(f"Esperado {atomo_msg[expected_type]}, encontrado {atomo_msg[self.lookahead.type]}")

    def parse(self):
        self.lookahead = self.lex.next_atom()
        self.programa()

    def programa(self):
        self.consume(PROGRAM)
        self.consume(IDENTIFIER)
        if self.lookahead.type == PARENTESES and self.lookahead.lexeme == '(':
            self.consume(PARENTESES)
            self.lista_de_identificadores()
            self.consume(PARENTESES)
        self.consume(PONTO_VIRG)
        self.bloco()
        self.consume(PONTO)

    def bloco(self):
        if self.lookahead.type == VAR:
            self.declaracoes_de_variaveis()
        self.comando_composto()

    def declaracoes_de_variaveis(self):
        self.consume(VAR)
        self.declaracao()
        self.consume(PONTO_VIRG)
        while self.lookahead.type == IDENTIFIER:
            self.declaracao()
            self.consume(PONTO_VIRG)

    def declaracao(self):
        self.lista_de_identificadores()
        self.consume(RELOP)  # ':' é um RELOP
        self.tipo()

    def lista_de_identificadores(self):
        self.consume(IDENTIFIER)
        while self.lookahead.type == VIRGULA:
            self.consume(VIRGULA)
            self.consume(IDENTIFIER)

    def tipo(self):
        if self.lookahead.type == INTEGER:
            self.consume(INTEGER)
        elif self.lookahead.type == BOOLEAN:
            self.consume(BOOLEAN)
        else:
            self.error("Tipo inválido")

    def comando_composto(self):
        self.consume(BEGIN)
        self.comando()
        while self.lookahead.type == PONTO_VIRG:
            self.consume(PONTO_VIRG)
            self.comando()
        self.consume(END)

    def comando(self):
        if self.lookahead.type == IDENTIFIER:
            self.atribuicao()
        elif self.lookahead.type == READ:
            self.comando_de_entrada()
        elif self.lookahead.type == WRITE:
            self.comando_de_saida()
        elif self.lookahead.type == IF:
            self.comando_if()
        elif self.lookahead.type == WHILE:
            self.comando_while()
        elif self.lookahead.type == BEGIN:
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
        if self.lookahead.type == ELSE:
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
        while self.lookahead.type == VIRGULA:
            self.consume(VIRGULA)
            self.expressao()
        self.consume(PARENTESES)

    def expressao(self):
        self.expressao_simples()
        if self.lookahead.type == RELOP:
            self.consume(RELOP)
            self.expressao_simples()

    def expressao_simples(self):
        if self.lookahead.type in [SUM, SUB]:
            self.consume(self.lookahead.type)
        self.termo()
        while self.lookahead.type in [SUM, SUB, ADDOP]:
            self.consume(self.lookahead.type)
            self.termo()

    def termo(self):
        self.fator()
        while self.lookahead.type in [MULT, DIV, MOD]:
            self.consume(self.lookahead.type)
            self.fator()

    def fator(self):
        if self.lookahead.type == IDENTIFIER:
            self.consume(IDENTIFIER)
        elif self.lookahead.type in [NUM_INT, NUM_REAL]:
            self.consume(self.lookahead.type)
        elif self.lookahead.type == PARENTESES and self.lookahead.lexeme == '(':
            self.consume(PARENTESES)
            self.expressao()
            self.consume(PARENTESES)
        elif self.lookahead.type == TRUE:
            self.consume(TRUE)
        elif self.lookahead.type == FALSE:
            self.consume(FALSE)
        elif self.lookahead.type == NOT:
            self.consume(NOT)
            self.fator()
        else:
            self.error("Fator inválido")
