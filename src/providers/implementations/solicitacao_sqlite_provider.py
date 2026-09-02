import uuid
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException, status

from ..interfaces.solicitacao_provider_interface import SolicitacaoProviderInterface
from ...models.solicitacao import Solicitacao
from ...models.status_local import StatusLocal

class SolicitacaoSqliteProvider(SolicitacaoProviderInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def criar_solicitacao(self, solicitacao: Dict[str, Any]) -> Dict[str, Any]:
        nova_solic = Solicitacao(
            id=str(uuid.uuid4())[:8],
            tipo=solicitacao.get('tipo', 'INSERIR'),
            especialidade=solicitacao.get('especialidade', ''),
            procedimento=solicitacao.get('procedimento', ''),
            codigo_paciente=int(solicitacao.get('codigo_paciente', 0)),
            nome_paciente=solicitacao.get('nome_paciente', ''),
            judicializado=solicitacao.get('judicializado', 'Não'),
            swallis=solicitacao.get('swallis', ''),
            medico_responsavel=solicitacao.get('medico_responsavel', ''),
            detalhes=solicitacao.get('detalhes', ''),
            tempo_standby=int(solicitacao.get('tempo_standby')) if solicitacao.get('tempo_standby') else None,
            status='PENDENTE',
            data_criacao=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            perfil_executor=solicitacao.get('perfil_executor', ''),
            usuario=solicitacao.get('usuario', ''),
            procedimento_anterior=solicitacao.get('procedimento_anterior', ''),
            origem_menu=solicitacao.get('origem_menu', 'Sistema LEC'),
            categorizacao=solicitacao.get('categorizacao', '') or None
        )
        
        self.session.add(nova_solic)
        await self.session.commit()
        
        # Retorna o dicionário
        return {
            'id': nova_solic.id,
            'tipo': nova_solic.tipo,
            'especialidade': nova_solic.especialidade,
            'procedimento': nova_solic.procedimento,
            'codigo_paciente': nova_solic.codigo_paciente,
            'nome_paciente': nova_solic.nome_paciente,
            'judicializado': nova_solic.judicializado,
            'swallis': nova_solic.swallis,
            'medico_responsavel': nova_solic.medico_responsavel,
            'detalhes': nova_solic.detalhes,
            'tempo_standby': nova_solic.tempo_standby,
            'status': nova_solic.status,
            'data_criacao': nova_solic.data_criacao,
            'perfil_executor': nova_solic.perfil_executor,
            'usuario': nova_solic.usuario,
            'procedimento_anterior': nova_solic.procedimento_anterior,
            'origem_menu': nova_solic.origem_menu,
            'categorizacao': nova_solic.categorizacao or ''
        }

    async def listar_solicitacoes(self) -> List[Dict[str, Any]]:
        stmt = select(Solicitacao)
        result = await self.session.execute(stmt)
        solicitacoes = result.scalars().all()
        
        return [
            {
                'id': s.id,
                'tipo': s.tipo,
                'especialidade': s.especialidade,
                'procedimento': s.procedimento,
                'codigo_paciente': s.codigo_paciente,
                'nome_paciente': s.nome_paciente,
                'judicializado': s.judicializado,
                'swallis': s.swallis,
                'medico_responsavel': s.medico_responsavel,
                'detalhes': s.detalhes,
                'tempo_standby': s.tempo_standby,
                'status': s.status,
                'data_criacao': s.data_criacao,
                'perfil_executor': s.perfil_executor,
                'usuario': getattr(s, 'usuario', '') or '',
                'procedimento_anterior': s.procedimento_anterior,
                'origem_menu': getattr(s, 'origem_menu', 'Sistema LEC') or 'Sistema LEC',
                'evento_tipo': getattr(s, 'evento_tipo', 'SOLICITACAO') or 'SOLICITACAO',
                'categorizacao': getattr(s, 'categorizacao', '') or ''
            }
            for s in solicitacoes
        ]

    async def atualizar_status_solicitacao(self, id_solicitacao: str, novo_status: str, perfil_executor: str = "", usuario_executor: str = "", justificativa: str = "") -> Dict[str, Any]:
        stmt = select(Solicitacao).where(Solicitacao.id == id_solicitacao)
        result = await self.session.execute(stmt)
        solic = result.scalar_one_or_none()
        
        if not solic:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada no SQLite")
            
        status_upper = novo_status.upper()
        solic.status = status_upper
        
        # Cria uma nova entrada no histórico representando especificamente a RESPOSTA
        data_resposta = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        acao_verb = "Aprovou" if status_upper == "APROVADO" else ("Cancelou" if status_upper == "CANCELADO" else "Rejeitou")
        
        if justificativa and justificativa.strip():
            detalhes_resposta = f"{acao_verb} a solicitação #{solic.id} ({solic.tipo}) - Justificativa: {justificativa.strip()}"
        else:
            detalhes_resposta = f"{acao_verb} a solicitação #{solic.id} ({solic.tipo})"

        resposta_solic = Solicitacao(
            id=str(uuid.uuid4())[:8],
            tipo=solic.tipo,
            especialidade=solic.especialidade,
            procedimento=solic.procedimento,
            codigo_paciente=solic.codigo_paciente,
            nome_paciente=solic.nome_paciente,
            judicializado=solic.judicializado,
            swallis=solic.swallis,
            medico_responsavel=solic.medico_responsavel,
            detalhes=detalhes_resposta,
            tempo_standby=solic.tempo_standby,
            status=status_upper,
            data_criacao=data_resposta,
            perfil_executor=perfil_executor or "GESTAO_LEC",
            usuario=usuario_executor or "GESTAO_LEC",
            procedimento_anterior=solic.procedimento_anterior,
            origem_menu=solic.origem_menu or "Sistema LEC",
            evento_tipo="RESPOSTA"
        )
        self.session.add(resposta_solic)
        await self.session.commit()
        
        return {
            'id': solic.id,
            'tipo': solic.tipo,
            'especialidade': solic.especialidade,
            'procedimento': solic.procedimento,
            'codigo_paciente': solic.codigo_paciente,
            'nome_paciente': solic.nome_paciente,
            'judicializado': solic.judicializado,
            'swallis': solic.swallis,
            'medico_responsavel': solic.medico_responsavel,
            'detalhes': solic.detalhes,
            'tempo_standby': solic.tempo_standby,
            'status': solic.status,
            'data_criacao': solic.data_criacao,
            'perfil_executor': solic.perfil_executor,
            'procedimento_anterior': solic.procedimento_anterior,
            'evento_tipo': 'SOLICITACAO',
            'detalhes_resposta': detalhes_resposta
        }

    async def editar_solicitacao(self, id_solicitacao: str, dados_atualizados: Dict[str, Any], perfil_executor: str = "", usuario_executor: str = "") -> Dict[str, Any]:
        stmt = select(Solicitacao).where(Solicitacao.id == id_solicitacao)
        result = await self.session.execute(stmt)
        solic = result.scalar_one_or_none()
        
        if not solic:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada")
            
        if solic.status != 'PENDENTE':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Apenas solicitações com status PENDENTE podem ser editadas.")
            
        if solic.tipo == 'EXCLUIR':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solicitações de exclusão não podem ser editadas, apenas canceladas.")

        # Rastreia campos alterados para histórico
        campos_alterados = []
        if 'especialidade' in dados_atualizados and dados_atualizados['especialidade'] and dados_atualizados['especialidade'] != solic.especialidade:
            campos_alterados.append(f"Especialidade: {solic.especialidade} -> {dados_atualizados['especialidade']}")
            solic.especialidade = dados_atualizados['especialidade']
            
        if 'procedimento' in dados_atualizados and dados_atualizados['procedimento'] and dados_atualizados['procedimento'] != solic.procedimento:
            campos_alterados.append(f"Procedimento: {solic.procedimento} -> {dados_atualizados['procedimento']}")
            solic.procedimento = dados_atualizados['procedimento']
            
        if 'judicializado' in dados_atualizados and dados_atualizados['judicializado'] != solic.judicializado:
            campos_alterados.append(f"Judicializado: {solic.judicializado} -> {dados_atualizados['judicializado']}")
            solic.judicializado = dados_atualizados['judicializado']
            
        if 'swallis' in dados_atualizados and dados_atualizados['swallis'] != solic.swallis:
            campos_alterados.append(f"Swalis: {solic.swallis} -> {dados_atualizados['swallis']}")
            solic.swallis = dados_atualizados['swallis']
            
        medico_alterado = False
        if 'medico_responsavel' in dados_atualizados and dados_atualizados['medico_responsavel'] != solic.medico_responsavel:
            campos_alterados.append(f"Médico: {solic.medico_responsavel} -> {dados_atualizados['medico_responsavel']}")
            solic.medico_responsavel = dados_atualizados['medico_responsavel']
            medico_alterado = True
            
        if 'categorizacao' in dados_atualizados:
            nova_cat = dados_atualizados['categorizacao'] or None
            if nova_cat != solic.categorizacao:
                campos_alterados.append(f"Categorização: {solic.categorizacao or 'Sem categorização'} -> {nova_cat or 'Sem categorização'}")
                solic.categorizacao = nova_cat
        elif medico_alterado and solic.categorizacao:
            campos_alterados.append("Categorização: Removida por alteração do médico responsável")
            solic.categorizacao = None
            
        if 'tempo_standby' in dados_atualizados and dados_atualizados['tempo_standby'] != solic.tempo_standby:
            novo_tempo = int(dados_atualizados['tempo_standby']) if dados_atualizados['tempo_standby'] else None
            campos_alterados.append(f"Standby: {solic.tempo_standby}d -> {novo_tempo}d")
            solic.tempo_standby = novo_tempo
            
        if 'detalhes' in dados_atualizados and dados_atualizados['detalhes']:
            solic.detalhes = dados_atualizados['detalhes']
            
        if 'procedimento_anterior' in dados_atualizados:
            solic.procedimento_anterior = dados_atualizados['procedimento_anterior']
            
        # O data_criacao original da solicitação permanece intacto para manter sua posição na fila
        data_alteracao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Cria uma nova linha no histórico representando a ação de ALTERAÇÃO
        resumo_mudancas = "; ".join(campos_alterados) if campos_alterados else "Atualização de justificativa/detalhes"
        detalhes_historico = f"Editou a solicitação #{solic.id} ({solic.tipo}) - {resumo_mudancas}. Justificativa: {solic.detalhes}"
        
        evento_alteracao = Solicitacao(
            id=str(uuid.uuid4())[:8],
            tipo=solic.tipo,
            especialidade=solic.especialidade,
            procedimento=solic.procedimento,
            codigo_paciente=solic.codigo_paciente,
            nome_paciente=solic.nome_paciente,
            judicializado=solic.judicializado,
            swallis=solic.swallis,
            medico_responsavel=solic.medico_responsavel,
            detalhes=detalhes_historico,
            tempo_standby=solic.tempo_standby,
            status='PENDENTE',
            data_criacao=data_alteracao,
            perfil_executor=perfil_executor or solic.perfil_executor,
            usuario=usuario_executor or solic.usuario,
            procedimento_anterior=solic.procedimento_anterior,
            origem_menu=solic.origem_menu or "Sistema LEC",
            evento_tipo="ALTERACAO",
            categorizacao=solic.categorizacao
        )
        self.session.add(evento_alteracao)
        await self.session.commit()
        
        return {
            'id': solic.id,
            'tipo': solic.tipo,
            'especialidade': solic.especialidade,
            'procedimento': solic.procedimento,
            'codigo_paciente': solic.codigo_paciente,
            'nome_paciente': solic.nome_paciente,
            'judicializado': solic.judicializado,
            'swallis': solic.swallis,
            'medico_responsavel': solic.medico_responsavel,
            'detalhes': solic.detalhes,
            'tempo_standby': solic.tempo_standby,
            'status': solic.status,
            'data_criacao': solic.data_criacao,
            'perfil_executor': solic.perfil_executor,
            'usuario': solic.usuario,
            'procedimento_anterior': solic.procedimento_anterior,
            'origem_menu': solic.origem_menu,
            'evento_tipo': 'SOLICITACAO',
            'categorizacao': solic.categorizacao or ''
        }

    async def salvar_status_local_paciente(self, codigo_paciente: str, status_local: str) -> Dict[str, Any]:
        cod_paciente_int = int(codigo_paciente)
        stmt = select(StatusLocal).where(StatusLocal.codigo_paciente == cod_paciente_int)
        result = await self.session.execute(stmt)
        s_local = result.scalar_one_or_none()
        
        data_atualizacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if s_local:
            s_local.status_local = status_local
            s_local.data_atualizacao = data_atualizacao
        else:
            s_local = StatusLocal(
                codigo_paciente=cod_paciente_int,
                status_local=status_local,
                data_atualizacao=data_atualizacao
            )
            self.session.add(s_local)
            
        await self.session.commit()
        
        return {
            'codigo_paciente': codigo_paciente,
            'status_local': status_local,
            'data_atualizacao': data_atualizacao
        }

    async def obter_status_locais_pacientes(self) -> Dict[str, str]:
        stmt = select(StatusLocal)
        result = await self.session.execute(stmt)
        status_list = result.scalars().all()
        return {str(s.codigo_paciente): s.status_local for s in status_list}
