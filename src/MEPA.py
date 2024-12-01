################################################################################
# PROVA FINAL - Prof: Leonardo Massayuki Takuno                                #
#                                                                              #
# Bruna Tiemi Tarumoto Watanabe - 1904272                                      #
# Gustavo Goes Sant'Ana - 2201501                                              #
# Kaiky Amorim dos Santos - 2200387                                            #
# Matheus Henrique Santos da Silva - 2200973                                   #
################################################################################

class MEPAInterpreter:
    def __init__(self):
        self.pilha = []   # Pilha para execução
        self.memoria = {} # Memória simulada
        self.codigo = []  # Código MEPA carregado
        self.ip = 0       # Instruction pointer
        self.arquivo_atual = None  # Nome do arquivo carregado
        self.codigo_modificado = False 

    #INTERATIVIDADE RELP (LIST/EXIT AQUI)
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
                    for i in range (0, len(self.codigo),20):
                        for j in range(i, min(i+20,len(self.codigo))):
                            print(f'{j+1}: {self.codigo [j]}')
                        if i+20 < len(self.codigo):
                            input("Pressione Enter para continuar")

            elif comando == "RUN":  
                if self.codigo:
                    print("\n--- Iniciando Execução ---")
                    self.executar()
                else:
                    print("Nenhum código carregado. Use o comando LOAD primeiro.")

            elif comando.startswith("INS"):
                partes = comando.split(maxsplit=2)  # Divide o comando em 3 partes: INS, <LINHA>, <INSTRUÇÃO>
                if len(partes) < 3:  # Verifica se há pelo menos 3 partes
                    print("Erro: O comando INS requer <LINHA> e <INSTRUÇÃO>. Exemplo: INS 30 CRCT 5")
                    continue     
                try:
                    linha = int(partes[1].strip())  # Remove espaços extras antes de converter
                    if linha < 0: # Verifica se a linha é negativa
                        print("Erro: A linha não pode ser negativa.")
                        continue
                    instrucao = partes[2].strip()  # Remove espaços extras na instrução
                    self.inserir_linha(linha, instrucao)  # Chama o método para inserir ou atualizar a linha
                except ValueError:
                    print(f"Erro ao converter linha para inteiro: '{partes[1]}'")
                    print("Erro: A linha deve ser um número inteiro válido.")

            elif comando.startswith("DEL"):
                partes = comando.split(maxsplit=2)  # Divide o comando em 3 partes: INS, <LINHA>, <INSTRUÇÃO>
                if len(partes) == 2:  # DEL <LINHA>
                    try:
                        linha = int(partes[1])
                        print("LINHAAA", linha)
                        self.del_linha(linha)
                    except ValueError:
                        print("Erro: A linha deve ser um número inteiro válido.")
                elif len(partes) == 3:  # DEL <LINHA_I> <LINHA_F>
                    try:
                        linha_i = int(partes[1])
                        linha_f = int(partes[2])
                        self.del_intervalo(linha_i, linha_f)
                    except ValueError:
                        print("Erro: As linhas devem ser números inteiros válidos.")

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
            
            elif comando == "DEBUG":
                print(self.codigo)
                if not self.codigo:
                    print("Nenhum código carregado.")
                else:
                    self.debug()

            elif comando == "EXIT":
                if self.codigo_modificado:
                    salvar = input("Há modificações não salvas. Deseja salvar? (S/N): ").strip().upper()
                    if salvar == "S":
                        if not self.salvar_codigo():
                            print("Erro ao salvar o código. O programa será encerrado sem salvar.")
                            continue
                print("Encerrando o programa.")
                break

            else:
                print("Comando inválido.")

    # DEL <LINHA>
    def del_linha(self, linha):
        if linha < 1 or linha > len(self.codigo):  # Verifica se a linha está fora do intervalo
            print(f"Erro: Linha {linha} inexistente.")
            return
        
        linha_removida = self.codigo.pop(linha-1) # Remove a linha 
        self.codigo_modificado = True
        print(f"Linha {linha} com a Instrução: {linha_removida} foi removida.") # Exibe a instrução removida

    # DEL <LINHA_I> <LINHA_F>
    def del_intervalo(self, linha_i, linha_f):
        if linha_i < 1 or linha_f < 1 or linha_i > len(self.codigo) or linha_f > len(self.codigo) or linha_i > linha_f:
            print("Erro: Intervalo inválido.")
            return
        
        linhas_removidas = self.codigo[linha_i - 1:linha_f]  # Ajusta para índice 0
        del self.codigo[linha_i - 1:linha_f]  # Remove as linhas do intervalo
        self.codigo_modificado = True
        print(f"Linhas removidas: {linha_i} a {linha_f}: Instruções removidas: {linhas_removidas}")

    #LOAD
    def carregar_codigo(self, codigo,arquivo=None):
        self.codigo = [linha.strip() for linha in codigo if linha.strip()]  # Remove espaços e linhas vazias
        self.arquivo_atual = arquivo
        self.codigo_modificado = False  # Reseta o status de modificação
        print(f"Código carregado com sucesso de '{arquivo}'." if arquivo else "Código carregado com sucesso.")

    #RUN 
    def executar(self):
        if not self.codigo:  # Verifica se há código carregado
            print("Nenhum código carregado. Use o comando 'LOAD <FILE_PATH>' primeiro.")
            return
           
        while self.ip < len(self.codigo):
            instrucao = self.codigo[self.ip]
            self.ip += 1
            try:
                self.executar_instrucao(instrucao)  # Chama o método para executar uma única instrução
            except Exception as e:
                print(f"Erro ao executar a instrução: {e}")
                break
        print("Execução concluída. Pilha final:", self.pilha)

    #INS
    def inserir_linha(self, linha, instrucao):
        # Verifica se a linha é negativa
        if linha < 0:
            print("Erro: A linha não pode ser negativa.")
            return
        
        # Verifica se a linha já existe
        for i, _ in enumerate(self.codigo):
            num_linha = i+1
            if int(num_linha) == linha:  # Linha já existe
                self.codigo[i] = f"{instrucao}"  # Atualiza a instrução
                self.codigo_modificado = True
                print(f"Linha {linha} atualizada.")
                return

        # Insere a nova linha na posição correta
        self.codigo.append(instrucao)  # Adiciona ao final
        self.codigo_modificado = True
        print(f"Linha {linha} inserida.")
        return

    #SAVE
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

    #DEBUG
    def debug(self):
        print("\n--- Modo de Depuração ---")
        while self.ip < len(self.codigo):
            instrucao = self.codigo[self.ip].strip()
            print(f"\nInstrução: {instrucao}")
            # Instrução atual

            # Aguarda o comando do usuário
            while True:
                comando = input("debug> ").strip().upper()
                if comando == "NEXT":
                    break
                elif comando == "STOP":
                    print("Saindo do modo de depuração.")
                    return
                elif comando == "STACK":
                    self.stack()  # Chama o método para exibir a memória e a pilha
                elif comando in ["LOAD", "RUN", "INS", "DEL", "EXIT"]:
                    print(f"Comando '{comando}' informado, modo de depuração finalizado!")
                    return
                else:
                    print("Comando inválido.")    
            
            # Executa a instrução
            self.ip += 1
            try:
                self.executar_instrucao(instrucao)  # Executa a instrução atual
                print("Modo de depuração encerrado devido à instrução (PARA).")
            except Exception as e:
                print(f"Erro ao executar a instrução: {e}")
                break

            # Mostra o estado atual da pilha e da memória

    #NEXT/STOP
    def executar_instrucao(self, instrucao):
        instrucao = instrucao.strip()
        if instrucao.startswith("INPP"):
            self.pilha = []  # Limpa a pilha
            self.memoria = {}  # Limpa a memória
            print("Programa iniciado (INPP).")

        elif instrucao.startswith("AMEM"):
            _, m = instrucao.split()
            for i in range(int(m)):
                self.memoria[len(self.memoria)] = 0
            print(f"Memória alocada: {m} posições.")

        elif instrucao.startswith("DMEM"):
            _, m = instrucao.split()
            for i in range(int(m)):
                if len(self.memoria) > 0:
                    self.memoria.pop(len(self.memoria) - 1)
            print(f"Memória desalocada: {m} posições.")

        elif instrucao.startswith("PARA"):
            print("Programa finalizado (PARA).")
            self.ip = len(self.codigo)  # Termina a execução

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
            self.ip = int(endereco) - 1

        elif instrucao.startswith("DSVF"):
            _, endereco = instrucao.split()
            condicao = self.pilha.pop()
            if condicao == 0:
                self.ip = int(endereco) - 1

        elif instrucao.startswith("NADA"):
            pass

        elif instrucao.startswith("IMPR"):
            valor = self.pilha.pop()
            print(f"IMPR: {valor}")

        else:
            raise Exception(f"Instrução inválida: {instrucao}")

    #STACK
    def stack(self):
        if not self.pilha:  # Verifica se a pilha está vazia
            print("A pilha está vazia.")
            return

        print("\n--- Conteúdo da Memória e da Pilha ---")
        print("Posição | Valor")
        print("----------------")
        for i in range(len(self.memoria)):  # Exibe toda a memória alocada
            valor = self.memoria.get(i, 0)  # Obtém o valor da posição i ou 0 se não estiver inicializada
            print(f"{i:7} | {valor}")
        print("\nTopo da Pilha:")
        for i, valor in enumerate(reversed(self.pilha)):  # Exibe os valores na pilha (do topo para a base)
            print(f"{len(self.pilha) - i - 1:7} | {valor}")
        print("----------------")

if __name__ == "__main__":
        interpreter = MEPAInterpreter()
        interpreter.repl()