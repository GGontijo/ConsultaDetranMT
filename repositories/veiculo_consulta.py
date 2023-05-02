from bs4 import BeautifulSoup
from helpers import tree_parser
from helpers.config_helper import *
from services.detran_selenium_service import DetranService
from services.secon_selenium_service import SeconService
from models.response_models import *


class VeiculoConsulta:

    def __init__(self) -> None:
        _config = Config()
        self.config = _config.get_config("VeiculoConsulta")
        self.driver_detran = DetranService()
        self.driver_secon = SeconService()

    def consulta_detran(self, placa: str, renavam: int):
        dados = {"placa": placa, "renavam": renavam}
        self.driver_detran.prepare(parameters=dados)
        self.driver_detran.run()
        _page = self.driver_detran.page_html

        #Busca os frames através do full XPath
        dados_veiculo_frame = tree_parser.get_frame(_page, '//*[@id="div_cabecalho"]')
        dados_multas_aberto_frame = tree_parser.get_frame(_page, '//*[@id="div_servicos_Multas"]/table')
        dados_autuacoes_frame = tree_parser.get_frame(_page, '/html/body/table/tbody/tr/td/div[4]/div/table') #Utilizando Full XPath pois tem dois frames com mesmo id
        dados_historico_autuacoes_frame = tree_parser.get_frame(_page, '/html/body/div[3]/div/table') #Utilizando Full XPath pois tem dois frames com mesmo id
        dados_historico_multas_frame = tree_parser.get_frame(_page, '//*[@id="div_servicos_HistoricoMultas"]/table')
        dados_multas_conveniadas_frame = tree_parser.get_frame(_page, '//*[@id="div_servicos_DebitosGestaoAutuador"]/table')
        dados_recursos_frame = tree_parser.get_frame(_page, '//*[@id="div_servicos_Recursos"]/table')
        dados_historico_processos_frame = tree_parser.get_frame(_page, '//*[@id="div_servicos_UltimoProcesso"]/table')
        dados_recall_frame = tree_parser.get_frame(_page, '//*[@id="div_servicos_Recall"]/table')
        dados_impedimentos_frame = tree_parser.get_frame(_page, '//*[@id="div_servicos_historicoimpedimento"]/table')
        
        dados = VeiculoConsultaSuccess()

        try:
            dados.Multa_Autuacao_Pendente = False
            dados_veiculos = {}
            for row in dados_veiculo_frame.findAll("tr"):
                cells = row.findAll("td")
                for cell in cells:
                    if len(cell.contents) == 3:
                        key = cell.contents[0].text.replace('\n', '').replace('\t', '').strip()
                        value = cell.contents[2].text.replace('\n', '').replace('\t', '').replace('\xa0', '').strip()
                    if len(cell.contents) < 3:
                        key = cell.contents[0].text.replace('\n', '').replace('\t', '').strip()
                        value = cell.contents[1].text.replace('\n', '').replace('\t', '').replace('\xa0', '').strip()
                    dados_veiculos[key] = value

        except AttributeError:
            response_error = {}
            if tree_parser.has_frame(_page, '/html/body/center/div/table/tbody/tr/td'):
                veiculo_not_found = tree_parser.get_frame(_page, '/html/body/center/div/table/tbody/tr/td')
                response_error = VeiculoConsultaError()
                response_error.detalhes = veiculo_not_found.text.replace('\n\n\t\t\t\t\t\t', ';').split(';')[1].strip()
            response_error.resultado = 'Não foi possível processar a requisição'
            response_error.success = False
            return response_error

        lista_dados_multas_aberto = []
        if tree_parser.has_frame(dados_multas_aberto_frame, '//*[@id="NaoTemNotificacao"]'):
            dados_multas_aberto = {}
            dados_multas_aberto['Situacao'] = dados_multas_aberto_frame.text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
            lista_dados_multas_aberto.append(dados_multas_aberto)
            if len(lista_dados_multas_aberto) == 1:
                lista_dados_multas_aberto = lista_dados_multas_aberto[0]
        else:
            for row in dados_multas_aberto_frame.find('tbody').contents:
                dados_multas_aberto = {}
                if row == '\n':
                    continue
                if hasattr(row, 'attrs') and len(row.attrs) > 0 and row.attrs['class'][0] == 'HeaderGrid':
                    continue
                if len(row.contents) <= 3:
                    dados_multas_aberto['Numero'] = row.contents[1].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[1].strip()
                dados_multas_aux = row.contents[1].text.replace('\n', ' ').replace('\t', '').replace('\xa0', '\n\n').replace('\n\n', ';').split(';')
                if len(dados_multas_aux) <= 5:
                    dados_multas_aberto['Numero'] = f'{dados_multas_aux[0].strip()} {dados_multas_aux[1].strip()}'
                    dados_multas_aberto['Situacao'] = dados_multas_aux[2].strip()
                if len(dados_multas_aux) > 5:
                    dados_multas_aberto['Numero'] = row.contents[1].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[1].strip()
                if dados_multas_aberto['Situacao'] == 'Em aberto':
                    dados.Multa_Autuacao_Pendente = True
                dados_multas_aberto['Descricao'] = row.contents[3].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
                dados_multas_aberto['Data_Infracao'] = row.contents[3].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[2].strip()
                dados_multas_aberto['Local_Infracao'] = row.contents[5].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
                dados_multas_aberto['Valor_Infracao'] = row.contents[7].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
                dados_multa_link_raw = row.contents[9].contents[1].attrs['onclick'].replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
                dados_multa = dados_multa_link_raw.split('(')[1].rstrip(')').replace("'", '').split(',')
                if len(dados_multa) == 1:
                    dados_multas_aberto['Url_Documento'] = f'https://internet.detrannet.mt.gov.br/rotinas/ConsultaImagemAIT.asp?IdRegistroLote={dados_multa[0]}'
                else:
                    dados_multas_aberto['Url_Documento'] = f'https://internet.detrannet.mt.gov.br/rotinas/NotificacaoAutoInfracao.asp?OrgaoAutuador={dados_multa[0]}&auto={dados_multa[1]}&codigoInfracao={dados_multa[2]}&Desdobramento={dados_multa[3]}&Placa={dados_multa[4]}&id={dados_multa[5]}'
                lista_dados_multas_aberto.append(dados_multas_aberto)
        
        lista_dados_autuacoes = []
        if tree_parser.has_frame(dados_autuacoes_frame, '//*[@id="NaoTemAutuacao"]'):
            dados_autuacoes = {}
            dados_autuacoes['Situacao'] = dados_autuacoes_frame.text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
            lista_dados_autuacoes.append(dados_autuacoes)
            if len(lista_dados_autuacoes) == 1:
                    lista_dados_autuacoes = lista_dados_autuacoes[0]
        else:
            for row in dados_autuacoes_frame.find('tbody').contents:
                dados_autuacoes = {}
                if row == '\n':
                    continue
                if hasattr(row, 'attrs') and len(row.attrs) > 0 and row.attrs['class'][0] == 'HeaderGrid':
                    continue
                if len(row.contents) <= 3:
                    dados_autuacoes['Numero'] = row.contents[1].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[1].strip()
                dados_autuacoes_aux = row.contents[1].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')
                if len(dados_autuacoes_aux) <= 5:
                    dados_autuacoes['Numero'] = f'{dados_autuacoes_aux[0].strip()} {dados_autuacoes_aux[1].strip()}'
                    dados_autuacoes['Situacao'] = dados_autuacoes_aux[3].strip()
                if len(dados_autuacoes_aux) > 5:
                    dados_autuacoes['Numero'] = row.contents[1].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[1].strip()
                    dados_autuacoes['Situacao'] = row.contents[1].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[3].strip()
                if dados_autuacoes['Situacao'] == 'Em aberto':
                    dados.Multa_Autuacao_Pendente = True
                dados_autuacoes['Descricao'] = row.contents[3].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
                dados_autuacoes['Data_Infracao'] = row.contents[3].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[1].strip()
                dados_autuacoes['Local_Infracao'] = row.contents[5].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[1].strip()
                dados_autuacoes['Valor_Infracao'] = row.contents[7].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
                dados_autuacao_raw = row.contents[9].contents[1].attrs['onclick'].replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
                dados_autuacao = dados_autuacao_raw.split('(')[1].rstrip(')').replace("'", '').split(',')
                if len(dados_autuacao) == 1:
                    dados_autuacoes['Url_Documento'] = f'https://internet.detrannet.mt.gov.br/rotinas/ConsultaImagemAIT.asp?IdRegistroLote={dados_autuacao[0]}'
                else:
                    dados_autuacoes['Url_Documento'] = f'https://internet.detrannet.mt.gov.br/rotinas/NotificacaoAutoInfracao.asp?OrgaoAutuador={dados_autuacao[0]}&auto={dados_autuacao[1]}&codigoInfracao={dados_autuacao[2]}&Desdobramento={dados_autuacao[3]}&Placa={dados_autuacao[4]}&id={dados_autuacao[5]}'
                lista_dados_autuacoes.append(dados_autuacoes)
            if len(lista_dados_autuacoes) == 1:
                lista_dados_autuacoes = lista_dados_autuacoes[0]


        lista_dados_historico_autuacoes = []
        if len(dados_historico_autuacoes_frame.find('tbody').contents) == 2:
            dados_historico_autuacoes = {}
            dados_historico_autuacoes['Situacao'] = dados_historico_autuacoes_frame.text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
            lista_dados_historico_autuacoes = dados_historico_autuacoes
        else:
            for row in dados_historico_autuacoes_frame.find('tbody').contents:
                if hasattr(row, 'attrs') and len(row.attrs) > 0 and row.attrs['class'][0] == 'HeaderGrid':
                    continue
                if row == '\n':
                    continue
                dados_historico_autuacoes = {}
                dados_historico_autuacoes['Numero'] = row.contents[1].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
                dados_historico_autuacoes['Situacao'] = row.contents[1].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[1].strip()
                dados_historico_autuacoes['Descricao'] = row.contents[3].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
                dados_historico_autuacoes['Data_Infracao'] = row.contents[3].text.replace('\n\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[1].strip()
                dados_historico_autuacoes['Local_Infracao'] = row.contents[5].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
                dados_historico_autuacoes['Valor_Infracao'] = row.contents[7].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
                dados_autuacao_raw = row.contents[9].contents[1].attrs['onclick'].replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
                dados_autuacao = dados_autuacao_raw.split('(')[1].rstrip(')').replace("'", '').split(',')
                if len(dados_autuacao) == 1:
                    dados_historico_autuacoes['Url_Documento'] = f'https://internet.detrannet.mt.gov.br/rotinas/ConsultaImagemAIT.asp?IdRegistroLote={dados_autuacao[0]}'
                else:
                    dados_historico_autuacoes['Url_Documento'] = f'https://internet.detrannet.mt.gov.br/rotinas/NotificacaoAutoInfracao.asp?OrgaoAutuador={dados_autuacao[0]}&auto={dados_autuacao[1]}&codigoInfracao={dados_autuacao[2]}&Desdobramento={dados_autuacao[3]}&Placa={dados_autuacao[4]}&id={dados_autuacao[5]}'
                lista_dados_historico_autuacoes.append(dados_historico_autuacoes)
            if len(lista_dados_historico_autuacoes) == 1:
                lista_dados_historico_autuacoes = lista_dados_historico_autuacoes[0]


        lista_dados_historico_multas = []
        if tree_parser.has_frame(dados_historico_multas_frame, '//*[@id="NaoTemAutuacao"]'):
            dados_historico_multas = {}
            dados_historico_multas['Situacao'] = dados_historico_multas_frame.text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
            lista_dados_historico_multas.append(dados_autuacoes)
            if len(lista_dados_historico_multas) == 1:
                    lista_dados_historico_multas = lista_dados_historico_multas[0]
        else:
            for row in dados_historico_multas_frame.find('tbody').contents:
                dados_historico_multas = {}
                if row == '\n':
                    continue
                if hasattr(row, 'attrs') and len(row.attrs) > 0 and row.attrs['class'][0] == 'HeaderGrid':
                    continue
                if len(row.contents) <= 3:
                    dados_historico_multas['Numero'] = row.contents[1].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[1].strip()
                dados_historico_multas_aux = row.contents[1].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')
                if len(dados_historico_multas_aux) <= 5:
                    dados_historico_multas['Numero'] = f'{dados_historico_multas_aux[0].strip()} {dados_historico_multas_aux[1].strip()}'
                    dados_historico_multas['Situacao'] = dados_historico_multas_aux[3].strip()
                if len(dados_historico_multas_aux) > 5:
                    dados_historico_multas['Numero'] = row.contents[1].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[1].strip()
                    dados_historico_multas['Situacao'] = row.contents[1].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[5].strip()
                dados_historico_multas['Data_Lancamento'] = row.contents[1].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[3].strip()
                dados_historico_multas['Descricao'] = row.contents[3].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[1].strip()
                dados_historico_multas['Data_Infracao'] = row.contents[3].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[3].strip()
                dados_historico_multas['Local_Infracao'] = row.contents[5].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
                dados_historico_multas['Valor_Infracao'] = row.contents[7].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
                dados_multa_link_raw = row.contents[9].contents[1].attrs['onclick'].replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
                dados_multa = dados_multa_link_raw.split('(')[1].rstrip(')').replace("'", '').split(',')
                if len(dados_multa) == 1:
                    dados_historico_multas['Url_Documento'] = f'https://internet.detrannet.mt.gov.br/rotinas/ConsultaImagemAIT.asp?IdRegistroLote={dados_multa[0]}'
                else:
                    dados_historico_multas['Url_Documento'] = f'https://internet.detrannet.mt.gov.br/rotinas/NotificacaoAutoInfracao.asp?OrgaoAutuador={dados_multa[0]}&auto={dados_multa[1]}&codigoInfracao={dados_multa[2]}&Desdobramento={dados_multa[3]}&Placa={dados_multa[4]}&id={dados_multa[5]}'
                lista_dados_historico_multas.append(dados_historico_multas)
            if len(lista_dados_historico_multas) == 1:
                lista_dados_historico_multas = lista_dados_historico_multas[0]

            
        lista_dados_multas_conveniadas = [] #TODO
        if tree_parser.has_frame(dados_multas_conveniadas_frame, '//*[@id="NaoTemDebitos"]'):
            dados_multas_conveniadas = {}
            dados_multas_conveniadas['Situacao'] = dados_multas_conveniadas_frame.text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
            lista_dados_multas_conveniadas.append(dados_multas_conveniadas)
            if len(lista_dados_multas_conveniadas) == 1:
                lista_dados_multas_conveniadas = lista_dados_multas_conveniadas[0]
        else:
            raise Exception('achamo!') #Falta mapear este


        lista_dados_recursos = []
        if len(dados_recursos_frame.find('tbody').contents) == 2:
            dados_recursos = {}
            dados_recursos['Situacao'] = dados_recursos_frame.text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
            lista_dados_recursos = dados_recursos
        else:
            for row in dados_recursos_frame.find('tbody').contents:
                if hasattr(row, 'attrs') and len(row.attrs) > 0 and row.attrs['class'][0] == 'HeaderGrid':
                    continue
                if row == '\n':
                    continue
                dados_recursos = {}
                dados_recursos['Processo'] = row.text.replace('\n\n', '\n').replace('\n\n\n', '\n').replace('\n\n\n\n', '\n').replace('\n\n\n\n\n', '\n').replace('\t', '').replace('\xa0', '').replace('\n', ';').replace(';;;;', ';').replace(';;', ';').replace(';;;', ';').split(';')[1].strip()
                dados_recursos['Data_Processo'] = row.text.replace('\n\n', '\n').replace('\n\n\n', '\n').replace('\n\n\n\n', '\n').replace('\n\n\n\n\n', '\n').replace('\t', '').replace('\xa0', '').replace('\n', ';').replace(';;;;', ';').replace(';;', ';').replace(';;;', ';').split(';')[2].strip()
                dados_recursos['Numero_do_Auto'] = row.text.replace('\n\n', '\n').replace('\n\n\n', '\n').replace('\n\n\n\n', '\n').replace('\n\n\n\n\n', '\n').replace('\t', '').replace('\xa0', '').replace('\n', ';').replace(';;;;', ';').replace(';;', ';').replace(';;;', ';').split(';')[3].strip()
                dados_recursos['Numero_Processo_Renainf'] = row.text.replace('\n\n', '\n').replace('\n\n\n', '\n').replace('\n\n\n\n', '\n').replace('\n\n\n\n\n', '\n').replace('\t', '').replace('\xa0', '').replace('\n', ';').replace(';;;;', ';').replace(';;', ';').replace(';;;', ';').split(';')[4].strip()
                dados_recursos['Motivo_Infracao'] = row.text.replace('\n\n', '\n').replace('\n\n\n', '\n').replace('\n\n\n\n', '\n').replace('\n\n\n\n\n', '\n').replace('\t', '').replace('\xa0', '').replace('\n', ';').replace(';;;;', ';').replace(';;', ';').replace(';;;', ';').split(';')[5].strip()
                dados_recursos['Data_Infracao'] = row.text.replace('\n\n', '\n').replace('\n\n\n', '\n').replace('\n\n\n\n', '\n').replace('\n\n\n\n\n', '\n').replace('\t', '').replace('\xa0', '').replace('\n', ';').replace(';;;;', ';').replace(';;', ';').replace(';;;', ';').split(';')[6].strip()
                dados_recursos['Local_Infracao'] = row.text.replace('\n\n', '\n').replace('\n\n\n', '\n').replace('\n\n\n\n', '\n').replace('\n\n\n\n\n', '\n').replace('\t', '').replace('\xa0', '').replace('\n', ';').replace(';;;;', ';').replace(';;', ';').replace(';;;', ';').split(';')[7].strip()
                dados_recursos['Resultado_Processo'] = row.text.replace('\n\n', '\n').replace('\n\n\n', '\n').replace('\n\n\n\n', '\n').replace('\n\n\n\n\n', '\n').replace('\t', '').replace('\xa0', '').replace('\n', ';').replace(';;;;', ';').replace(';;', ';').replace(';;;', ';').split(';')[8].strip()
                lista_dados_recursos.append(dados_recursos)
            if len(lista_dados_recursos) == 1:
                lista_dados_recursos = lista_dados_recursos[0]


        #lista_dados_historico_processos = [] -> Vou deixar de fora visto que não é relevante até o momento, estrutura complexa.
        #for row in dados_historico_processos_frame.contents[1].contents[1].contents:
        #    dados_historico_processos = {}
        #    if row == '\n':
        #        continue
        #    if hasattr(row, 'attrs') and len(row.attrs) > 0 and row.attrs['class'][0] == 'HeaderGrid':
        #        continue
        #    teste = row.contents[7].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')
        #    dados_historico_processos['Processo'] = row.contents[1].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[1].strip()
        #    dados_historico_processos['Interessado'] = row.contents[3].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
        #    dados_historico_processos['Servico'] = row.contents[5].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
        #    dados_historico_processos['Data_Operacao'] = row.contents[7].text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
        #    lista_dados_historico_processos.append(dados_historico_processos)

        lista_dados_recall = []
        if len(dados_recall_frame.find('tbody').contents) == 2:
            dados_recall = {}
            dados_recall['Situacao'] = dados_recall_frame.text.replace('\n\t\t', ';').replace('\n', ' ').replace('\t', '').replace('\xa0', '').split(';')[0].strip()
            lista_dados_recall = dados_recall
        else:
            for row in dados_recall_frame.find('tbody').contents:
                dados_recall = {}
                if hasattr(row, 'attrs') and len(row.attrs) > 0 and row.attrs['class'][0] == 'HeaderGrid':
                    continue
                if row == '\n':
                    continue
                dados_recall['ID_Recall'] = row.text.replace('\n', ';').split(';')[1].strip()
                dados_recall['Nome_Recall'] = row.text.replace('\n', ';').split(';')[2].strip()
                dados_recall['Defeito'] = row.text.replace('\n', ';').split(';')[3].strip()
                dados_recall['Ata_Registro'] = row.text.replace('\n', ';').split(';')[4].strip()
                dados_recall['Prazo_Serviço'] = row.text.replace('\n', ';').split(';')[5].strip()
                dados_recall['Situacao'] = row.text.replace('\n', ';').split(';')[6].strip()
                dados_recall['Concessionaria'] = row.text.replace('\n', ';').split(';')[7].strip()
                dados_recall['Realizado_em'] = row.text.replace('\n', ';').split(';')[8].strip()
                dados_recall['Data_Inclusao'] = row.text.replace('\n', ';').split(';')[9].strip()
                lista_dados_recall.append(dados_recall)
            if len(lista_dados_recall) == 1:
                lista_dados_recall = lista_dados_recall[0]


        if len(dados_impedimentos_frame.find('tbody').contents) == 2:
            dados_impedimentos = {}
            dados_impedimentos['Situacao'] = dados_impedimentos_frame.text.replace('\n\n', ';').replace('\n', '').replace('\t', '').replace('\xa0', '').split(';')[1].strip()
        else:
            dados_impedimentos = {}
            for row in dados_impedimentos_frame.findAll("tr"):
                cells = row.findAll("td")
                for cell in cells:
                    if len(cell.contents) == 0:
                        continue
                    if len(cell.contents) == 3:
                        key = cell.contents[0].text.replace('\n', '').replace('\t', '').replace('ã', 'a').replace('ç', 'c').replace('á', 'a').replace(' ', '_').replace('/', '_').strip()
                        value = cell.contents[2].text.replace('\n', '').replace('\t', '').replace('\xa0', '').strip()
                    if len(cell.contents) < 3:
                        key = cell.contents[0].text.replace('\n', '').replace('\t', '').replace('ã', 'a').replace('ç', 'c').replace('á', 'a').replace(' ', '_').replace('/', '_').strip()
                        value = cell.contents[1].text.replace('\n', '').replace('\t', '').replace('\xa0', '').strip()
                    dados_impedimentos[key] = value
            
        
        dados.dados_veiculos = dados_veiculos
        dados.dados_multas_aberto = lista_dados_multas_aberto
        dados.dados_autuacoes_aberto = lista_dados_autuacoes
        dados.dados_historico_multas = lista_dados_historico_multas
        dados.dados_multas_conveniadas = lista_dados_multas_conveniadas
        dados.dados_recursos = lista_dados_recursos
        #dados['dados_historico_processos'] = dados_historico_processos
        dados.dados_recall = lista_dados_recall
        dados.dados_impedimentos = dados_impedimentos
        dados.success = True

        return dados

    def consulta_secon(self, placa: str, renavam: int):
        dados = {"placa": placa, "renavam": renavam}
        self.driver_secon.prepare(parameters=dados)
        self.driver_secon.run()
        ##Daqui pra baixo estou assumindo que esteja usando apenas o detran, é preciso fazer duas rotas de scrapping
        ##Colocar delay de execução entre consultas para o site não entender como spam
        parsed_page = BeautifulSoup(self.driver_secon.page_html, 'html.parser')
        parsed_frame = parsed_page.find('body')
        historico_multa_div = parsed_frame.find('div', {'id': 'div_servicos_HistoricoMultas'})
        historico_multa_body = historico_multa_div.find('td').find_next_sibling("td").text
        print(historico_multa_body)