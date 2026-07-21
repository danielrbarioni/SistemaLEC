import os
import csv
import uuid
from datetime import datetime
from typing import List, Dict, Any
from fastapi import HTTPException, status

from ..interfaces.solicitacao_provider_interface import SolicitacaoProviderInterface

class SolicitacaoCsvProvider(SolicitacaoProviderInterface):
    def __init__(
        self, 
        solicitacoes_path: str = 'data/solicitacoes.csv',
        status_locais_path: str = 'data/status_locais.csv'
    ):
        self.solicitacoes_path = solicitacoes_path
        self.status_locais_path = status_locais_path
        self._initialize_files()

    def _initialize_files(self):
        # Garante que a pasta data exista
        os.makedirs('data', exist_ok=True)
        
        # Inicializa arquivo de solicitações
        if not os.path.exists(self.solicitacoes_path):
            with open(self.solicitacoes_path, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'tipo', 'especialidade', 'procedimento', 'codigo_paciente', 'nome_paciente', 'judicializado', 'swalis', 'medico_responsavel', 'detalhes', 'tempo_standby', 'status', 'data_criacao', 'perfil_executor', 'usuario', 'procedimento_anterior', 'data_acao'])
        else:
            # Verifica se precisa adicionar as novas colunas
            with open(self.solicitacoes_path, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, [])
            if 'perfil_executor' not in header or 'usuario' not in header or 'procedimento_anterior' not in header or 'data_acao' not in header:
                solics = []
                with open(self.solicitacoes_path, mode='r', encoding='utf-8') as f:
                    r = csv.DictReader(f)
                    for row in r:
                        if 'perfil_executor' not in row:
                            row['perfil_executor'] = ''
                        if 'usuario' not in row:
                            row['usuario'] = ''
                        if 'procedimento_anterior' not in row:
                            row['procedimento_anterior'] = ''
                        if 'data_acao' not in row:
                            row['data_acao'] = ''
                        solics.append(row)
                with open(self.solicitacoes_path, mode='w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['id', 'tipo', 'especialidade', 'procedimento', 'codigo_paciente', 'nome_paciente', 'judicializado', 'swalis', 'medico_responsavel', 'detalhes', 'tempo_standby', 'status', 'data_criacao', 'perfil_executor', 'usuario', 'procedimento_anterior', 'data_acao'])
                    writer.writeheader()
                    writer.writerows(solics)

        # Inicializa arquivo de status locais
        if not os.path.exists(self.status_locais_path):
            with open(self.status_locais_path, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['codigo_paciente', 'status_local', 'data_atualizacao'])

    async def criar_solicitacao(self, solicitacao: Dict[str, Any]) -> Dict[str, Any]:
        nova_solic = {
            'id': str(uuid.uuid4())[:8],
            'tipo': solicitacao.get('tipo', 'INSERIR'),
            'especialidade': solicitacao.get('especialidade', ''),
            'procedimento': solicitacao.get('procedimento', ''),
            'codigo_paciente': str(solicitacao.get('codigo_paciente', '')),
            'nome_paciente': solicitacao.get('nome_paciente', ''),
            'judicializado': solicitacao.get('judicializado', 'Não'),
            'swalis': solicitacao.get('swalis') or solicitacao.get('swallis') or '',
            'medico_responsavel': solicitacao.get('medico_responsavel', ''),
            'detalhes': solicitacao.get('detalhes', ''),
            'tempo_standby': solicitacao.get('tempo_standby', ''),
            'status': 'PENDENTE',
            'data_criacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'perfil_executor': solicitacao.get('perfil_executor', ''),
            'usuario': solicitacao.get('usuario', ''),
            'procedimento_anterior': solicitacao.get('procedimento_anterior', ''),
            'data_acao': ''
        }
        
        with open(self.solicitacoes_path, mode='a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=nova_solic.keys())
            writer.writerow(nova_solic)
            
        return nova_solic

    async def listar_solicitacoes(self) -> List[Dict[str, Any]]:
        solicitacoes = []
        if not os.path.exists(self.solicitacoes_path):
            return solicitacoes
            
        with open(self.solicitacoes_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                solicitacoes.append(row)
        return solicitacoes

    async def atualizar_status_solicitacao(self, id_solicitacao: str, novo_status: str) -> Dict[str, Any]:
        solicitacoes = await self.listar_solicitacoes()
        encontrado = False
        solicitacao_atualizada = {}
        
        for solic in solicitacoes:
            if solic['id'] == id_solicitacao:
                solic['status'] = novo_status.upper()
                solic['data_acao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                solicitacao_atualizada = solic
                encontrado = True
                break
                
        if not encontrado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada")
            
        # Re-escrever o arquivo
        with open(self.solicitacoes_path, mode='w', encoding='utf-8', newline='') as f:
            if solicitacoes:
                writer = csv.DictWriter(f, fieldnames=solicitacoes[0].keys())
                writer.writeheader()
                writer.writerows(solicitacoes)
                
        return solicitacao_atualizada

    async def salvar_status_local_paciente(self, codigo_paciente: str, status_local: str) -> Dict[str, Any]:
        status_atualizados = []
        encontrado = False
        data_atualizacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if os.path.exists(self.status_locais_path):
            with open(self.status_locais_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    status_atualizados.append(row)

        for s in status_atualizados:
            if s['codigo_paciente'] == str(codigo_paciente):
                s['status_local'] = status_local
                s['data_atualizacao'] = data_atualizacao
                encontrado = True
                break
                
        if not encontrado:
            status_atualizados.append({
                'codigo_paciente': str(codigo_paciente),
                'status_local': status_local,
                'data_atualizacao': data_atualizacao
            })
            
        with open(self.status_locais_path, mode='w', encoding='utf-8', newline='') as f:
            if status_atualizados:
                writer = csv.DictWriter(f, fieldnames=status_atualizados[0].keys())
                writer.writeheader()
                writer.writerows(status_atualizados)
                
        return {
            'codigo_paciente': codigo_paciente,
            'status_local': status_local,
            'data_atualizacao': data_atualizacao
        }

    async def obter_status_locais_pacientes(self) -> Dict[str, str]:
        mapeamento = {}
        if not os.path.exists(self.status_locais_path):
            return mapeamento
            
        with open(self.status_locais_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                mapeamento[row['codigo_paciente']] = row['status_local']
        return mapeamento
