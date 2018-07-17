#coding=UTF-8
import os
import json
from kivy.app import App

class ControleRede(App):
    history_comando = []

    password = ""
    '''
    Mapeamento dos Host
    '''
    host={'h1':'00:00:00:00:00:01',
          'h2':'00:00:00:00:00:02',
          'h3':'00:00:00:00:00:03',
          'h4':'00:00:00:00:00:04',
          'WebServer':'00:00:00:00:00:11',
          'IPTV':'00:00:00:00:00:12'}
    '''
    Mapeamento dos Swicth
    '''
    switch={'s1':['1','2','13','14'],
            's2':['1','2','13','14'],
            's3':['1', '2','11','12','14'],
            's4':['11','12','13']}

    '''
    Mapemento das Conexões
    '''
    conexoes={'h1':'s1',
              'h2': 's1',
              'h3': 's2',
              'h4': 's2',
              'WebServer':'s3',
              'IPTV':'s3'}
    '''
    Mapeamento dos Links
    '''
    principal={'s1':'13',
               's2':'13',
               's3':['11','12']}

    backup={'s1':'14',
            's2':'14',
            's3':'14'}

    ###Guarda a senha de ROOT
    def obterSenhaRoot(self):
        parametro = self.root.ids.campo_password
        self.__class__.password = parametro.text
        parametro.text = ""
    ###Executa um comando passado e retorna o texto obtido
    def command(self):
        ####Guarda o Comando em uma Lista#######
        self.__class__.history_comando.append(self.root.ids.campo_comando_entrada.text)

        ####Limpa o Campo de Saida#####
        self.root.ids.campo_saida_comando.text = ""


        comando = self.root.ids.campo_comando_entrada.text
        text = os.popen("echo %s | sudo -S %s" % (self.__class__.password, comando))
        self.root.ids.campo_comando_entrada.text=""#####Limpa o campo de comando
        for i  in text:
            self.root.ids.campo_saida_comando.text += i
        #return text

    ####Retorna as portas de um determinado Switch
    def listaPortasSwitch(self):
        switch = self.root.ids.switch.text
        if(switch !='Selecione o Switch' ):
            self.root.ids.porta.values = self.__class__.switch[switch]
        else:
            self.root.ids.porta.vlaues = "Selecione a Porta"


    ####Retorna a Lista de Comandos ja executados
    def listaComandosExecutados(self):
        r = self.root.ids.lista_comandos
        self.__class__.history_comando = list(set(self.__class__.history_comando)) ###Retira os comandos repetidos
        r.values =self.__class__.history_comando

    ####Joga o camando selecionado na Lista de comando no campo executar
    def retornaComandoSelecionado(self):
        r = self.root.ids.lista_comandos
        if(r.text != "Comandos Executados"):
            self.root.ids.campo_comando_entrada.text = r.text
            r.text = "Comandos Executados"
        else:
            self.root.ids.campo_comando_entrada.text = ""

    '''
    Comandos executados para ovs
    '''
    ####Execucao dos comandos ovs
    def executaComandosOVS(self,comando):
        text = os.popen("echo %s | sudo -S %s" % (self.__class__.password, comando))
        for i in text:
            self.root.ids.campo_saida_comando.text += i


    ####Obtem as entradas selecionadas
    def obterDadosEntrada(self):
        switch = self.root.ids.switch.text
        host = self.root.ids.host.text
        porta = self.root.ids.porta.text
        lista={'switch':switch,
               'host':host,
               'porta':porta}
        return lista

    ####sudo ovs-ofctl add-flow
    def adicionaUmFluxo(self):
        lista = self.obterDadosEntrada()
        mac = self.__class__.host[lista['host']]
        comando = 'ovs-ofctl add-flow '+lista['switch']+' dl_dst='+mac+',actions=output:'+lista['porta']
        self.executaComandosOVS(comando)

    '''
    Comando: ovs-ofctl dump-flows s1
    Lista os fluxos de determinado Switch
    '''
    def listarFluxosSwitch(self):
        self.root.ids.campo_saida_comando.text=""
        lista = self.obterDadosEntrada()
        switch = lista['switch']
        comando = 'ovs-ofctl dump-flows '+switch
        self.executaComandosOVS(comando)

    '''
    Comando:ovs-ofctl del-flows br0
    Apaga os fluxo de um determinado Switch
    '''
    def apagaFluxosSwitch(self):
        self.root.ids.campo_saida_comando.text = ""
        lista = self.obterDadosEntrada()
        switch = lista['switch']
        comando = 'ovs-ofctl del-flows '+switch
        self.executaComandosOVS(comando)

    ##### Mudar todo fluxo da rede Host Origem para Host Destino################
    def montaComando_Executa(self,switch,mac_origem,mac_destino,porta):
        comando = 'ovs-ofctl add-flow '+ switch +' dl_src='+mac_origem+',dl_dst='+mac_destino+',actions=output:'+porta
        self.executaComandosOVS(comando)
        return comando

    ##### Encontra a porta de saida#########
    def portaSwitch(self,host_origem,host_destino,switch_origem,switch_destino,link):
        porta = ''
        if(switch_origem == 's1' and switch_destino == 's1'):
            if host_origem == 'h1':
                porta = '2'
            elif host_origem == 'h2':
                porta = '1'
        elif ((switch_origem == 's1' and switch_destino =='s2') or (switch_origem == 's1' and switch_destino =='s3')):
            if link == 'Principal':
                porta = '13'
            elif link == 'Backup':
                porta = '14'
        elif(switch_origem == 's2' and switch_destino == 's2'):
            if host_origem == 'h3':
                porta = '2'
            elif host_origem == 'h4':
                porta = '1'
        elif((switch_origem == 's2' and switch_destino =='s1') or (switch_origem == 's2' and switch_destino =='s3')):
            if link == 'Principal':
                porta = '13'
            elif link == 'Backup':
                porta = '14'
        elif(switch_origem == 's3' and switch_destino == 's3'):
            if host_origem == 'WebServer':
                porta = '2'
            elif host_origem == 'IPTV':
                porta = '1'
        elif(switch_origem == 's3' and switch_destino =='s1'):
            if link == 'Principal':
                porta = '11'
            elif link == 'Backup':
                porta = '14'

        elif(switch_origem == 's3' and switch_destino =='s2'):
            if link == 'Principal':
                porta = '12'
            elif link == 'Backup':
                porta = '14'
        return porta

    ######## Altera Tráfego Geral entre dois Host (Ambos os fluxos tanto RX como TX) ###################
    def alterarTodoFluxoRede(self):
        self.root.ids.campo_saida_comando.text = ''
        host_origem = self.root.ids.hostOrigem.text
        host_destino = self.root.ids.hostDestino.text
        link = self.root.ids.link.text
        if(host_origem == 'Selecione' or host_destino == 'Selecione' or link == 'Selecione'):
            self.root.ids.campo_saida_comando.text = 'ERRO!!!\nPor Favor, selecione todos os campos!!!'
        else:
            mac_origem = self.__class__.host[host_origem]
            mac_destino = self.__class__.host[host_destino]
            switch_origem = self.__class__.conexoes[host_origem] ###Switch onde esta conectado o Host Origem
            switch_destino = self.__class__.conexoes[host_destino]###Switch onde esta conextado o Host Destino
            if(switch_origem != switch_destino):
                comando1 = self.montaComando_Executa(switch_origem,mac_origem,mac_destino,self.portaSwitch(host_origem,host_destino,switch_origem,switch_destino,link))
                print(comando1)
                self.__class__.history_comando.append(comando1)
                self.root.ids.campo_saida_comando.text=comando1
                comando2 = self.montaComando_Executa(switch_destino,mac_destino,mac_origem,self.portaSwitch(host_destino,host_origem,switch_destino,switch_origem,link))
                print(comando2)
                self.__class__.history_comando.append(comando1)
                self.root.ids.campo_saida_comando.text+= '\n'+comando2
                self.root.ids.campo_saida_comando.text+='\n\n\nFLUXO ALTERADO!!'
            else:
                self.root.ids.campo_saida_comando.text = "Os Hosts selecionados estão no mesmo Switch!!!\n\n\nFLUXO INALTERADO!!!"
    ######## Altera o TX #########################
    def alterarTX(self):
        self.root.ids.campo_saida_comando.text = ''
        host_origem = self.root.ids.hostOrigem.text
        host_destino = self.root.ids.hostDestino.text
        link = self.root.ids.link.text
        if (host_origem == 'Selecione' or host_destino == 'Selecione' or link == 'Selecione'):
            self.root.ids.campo_saida_comando.text = 'ERRO!!!\nPor Favor, selecione todos os campos!!!'
        else:
            mac_origem = self.__class__.host[host_origem]
            mac_destino = self.__class__.host[host_destino]
            switch_origem = self.__class__.conexoes[host_origem]  ###Switch onde esta conectado o Host Origem
            switch_destino = self.__class__.conexoes[host_destino]  ###Switch onde esta conextado o Host Destino
            if(switch_origem != switch_destino):
                comando = self.montaComando_Executa(switch_origem,mac_origem,mac_destino,self.portaSwitch(host_destino,host_origem,switch_destino,switch_origem,link))
                print(comando)
                self.root.ids.campo_saida_comando.text = comando
                self.root.ids.campo_saida_comando.text += '\n\n\nFLUXO ALTERADO'
                self.__class__.history_comando.append(comando)
            else:
                self.root.ids.campo_saida_comando.text = "Os Hosts selecionados estão no mesmo Switch!!!\n\n\nFLUXO INALTERADO!!!"

    ######## Altera o RX ###########################
    def alterarRX(self):
        self.root.ids.campo_saida_comando.text = ''
        host_origem = self.root.ids.hostOrigem.text
        host_destino = self.root.ids.hostDestino.text
        link = self.root.ids.link.text
        if (host_origem == 'Selecione' or host_destino == 'Selecione' or link == 'Selecione'):
            self.root.ids.campo_saida_comando.text = 'ERRO!!!\nPor Favor, selecione todos os campos!!!'
        else:
            mac_origem = self.__class__.host[host_origem]
            mac_destino = self.__class__.host[host_destino]
            switch_origem = self.__class__.conexoes[host_origem]  ###Switch onde esta conectado o Host Origem
            switch_destino = self.__class__.conexoes[host_destino]  ###Switch onde esta conextado o Host Destino
            if(switch_origem != switch_destino):
                comando = self.montaComando_Executa(switch_destino,mac_destino,mac_origem,self.portaSwitch(host_destino,host_origem,switch_destino,switch_origem,link))
                print(comando)
                self.root.ids.campo_saida_comando.text = comando
                self.root.ids.campo_saida_comando.text+='\n\n\nFLUXO ALTERADO'
                self.__class__.history_comando.append(comando)
            else:
                self.root.ids.campo_saida_comando.text = "Os Hosts selecionados estão no mesmo Switch!!!\n\n\nFLUXO INALTERADO!!!"

    ################ Altera todo tráfego Geral de um determinado Host#########################
    def alterTrafegoHostCompleto(self):
        self.root.ids.campo_saida_comando.text = ''
        host = self.root.ids.host_select.text
        link = self.root.ids.link_select.text
        if(host != 'Selecione o Host' and link != 'Selecione o Link' ):
            mac = self.__class__.host[host]
            switch_origem = self.__class__.conexoes[host]
            with open('MapeamentoComandos.json','r') as f:
                r = json.load(f)
                for i in r:
                    lista = i.split('_')
                    if(lista[0] == host or lista[2]==host):
                        if(link == 'Principal'):
                            self.executaComandosOVS(r[i])
                            self.root.ids.campo_saida_comando.text+=r[i]+'\n'
                            self.__class__.history_comando.append(r[i])
                        elif(link == 'Backup'):
                            lista2 = r[i].split(':')
                            lista2[len(lista2)-1] = '14'
                            comando = ''
                            cont = 0
                            for j in lista2:
                                if(cont == 0):
                                    comando = j
                                else:
                                    comando = comando + ':' +j
                                cont = cont +1
                            self.executaComandosOVS(comando)
                            self.root.ids.campo_saida_comando.text += comando + '\n'
                            self.__class__.history_comando.append(comando)
        elif(host == 'Selecione o Host' or link == 'Selecione o Link' ):
            self.root.ids.campo_saida_comando.text='ERRO!!!\n\n\nPor Favor, selecione todos os Campos!!!'
    ################ FIM Altera todo tráfego Geral de um determinado Host#########################

    ################# Alterando todo TX de um Host ###########################
    def alterarTrafegoTXHost(self):
        self.root.ids.campo_saida_comando.text = ''
        host = self.root.ids.host_select.text
        link = self.root.ids.link_select.text
        if (host != 'Selecione o Host' and link != 'Selecione o Link'):
            mac = self.__class__.host[host]
            switch_origem = self.__class__.conexoes[host]
            with open('MapeamentoComandos.json', 'r') as f:
                r = json.load(f)
            for i in r:
                lista = i.split('_')
                if(lista[0] == host):
                    if(link == 'Principal'):
                        self.executaComandosOVS(r[i])
                        self.root.ids.campo_saida_comando.text += r[i] + '\n'
                        self.__class__.history_comando.append(r[i])
                    elif(link == 'Backup'):
                        lista2 = r[i].split(':')
                        lista2[len(lista2) - 1] = '14'
                        comando = ''
                        cont = 0
                        for j in lista2:
                            if (cont == 0):
                                comando = j
                            else:
                                comando = comando + ':' + j
                            cont = cont + 1
                        self.executaComandosOVS(comando)
                        self.root.ids.campo_saida_comando.text += comando + '\n'
                        self.__class__.history_comando.append(comando)
        elif (host == 'Selecione o Host' or link == 'Selecione o Link'):
            self.root.ids.campo_saida_comando.text = 'ERRO!!!\n\n\nPor Favor, selecione todos os Campos!!!'

    ################# FIM Alterando todo TX de um Host ###########################

    ################# Alterando todo RX de um Host ###########################
    def alterarTrafegoRXHost(self):
        self.root.ids.campo_saida_comando.text = ''
        host = self.root.ids.host_select.text
        link = self.root.ids.link_select.text
        if (host != 'Selecione o Host' and link != 'Selecione o Link'):
            mac = self.__class__.host[host]
            switch_origem = self.__class__.conexoes[host]
            with open('MapeamentoComandos.json', 'r') as f:
                r = json.load(f)
            for i in r:
                lista = i.split('_')
                if (lista[2] == host):
                    if (link == 'Principal'):
                        self.executaComandosOVS(r[i])
                        self.root.ids.campo_saida_comando.text += r[i] + '\n'
                        self.__class__.history_comando.append(r[i])
                    elif (link == 'Backup'):
                        lista2 = r[i].split(':')
                        lista2[len(lista2) - 1] = '14'
                        comando = ''
                        cont = 0
                        for j in lista2:
                            if (cont == 0):
                                comando = j
                            else:
                                comando = comando + ':' + j
                            cont = cont + 1
                        self.executaComandosOVS(comando)
                        self.root.ids.campo_saida_comando.text += comando + '\n'
                        self.__class__.history_comando.append(comando)
        elif (host == 'Selecione o Host' or link == 'Selecione o Link'):
            self.root.ids.campo_saida_comando.text = 'ERRO!!!\n\n\nPor Favor, selecione todos os Campos!!!'
    ################# FIM Alterando todo RX de um Host ###########################



##################END CLASS#####################################

janela = ControleRede()
janela.run()