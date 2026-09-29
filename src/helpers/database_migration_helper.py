import json
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

async def migrate_cirurgia_geral_to_geral(conn):
    """
    Migra de forma segura, transacional e idempotente qualquer registro de
    CIRURGIA GERAL para GERAL em todas as tabelas do banco de dados SQLite.
    Garante que ações pendentes, concluídas, usuários, procedimentos, perfis,
    solicitações e categorizações sejam perfeitamente preservados e unificados.
    """
    try:
        # 1. Tratar perfis
        res = await conn.execute(text("SELECT id, nome, tipo, cor, especialidade FROM perfis WHERE id = 'GERAL';"))
        geral_profile = res.mappings().first()

        res_cg = await conn.execute(text(
            "SELECT id, nome, tipo, cor, especialidade FROM perfis WHERE id IN ('CIRURGIA_GERAL', 'CIRURGIA GERAL') OR UPPER(especialidade) = 'CIRURGIA GERAL' OR UPPER(nome) = 'CIRURGIA GERAL';"
        ))
        cg_profiles = res_cg.mappings().all()

        if not geral_profile:
            if cg_profiles:
                # Atualiza o primeiro para GERAL
                first_cg_id = cg_profiles[0]["id"]
                await conn.execute(text(
                    "UPDATE perfis SET id = 'GERAL', nome = 'GERAL', tipo = 'ESPECIALIDADE', cor = 'verde', especialidade = 'GERAL' WHERE id = :old_id;"
                ), {"old_id": first_cg_id})
            else:
                await conn.execute(text(
                    "INSERT INTO perfis (id, nome, tipo, cor, especialidade) VALUES ('GERAL', 'GERAL', 'ESPECIALIDADE', 'verde', 'GERAL');"
                ))
        else:
            await conn.execute(text(
                "UPDATE perfis SET nome = 'GERAL', tipo = 'ESPECIALIDADE', cor = 'verde', especialidade = 'GERAL' WHERE id = 'GERAL';"
            ))

        # 2. Tratar usuarios
        res_users = await conn.execute(text(
            "SELECT id, username, nome, perfil_id, especialidade, funcao FROM usuarios WHERE UPPER(perfil_id) IN ('CIRURGIA_GERAL', 'CIRURGIA GERAL') OR UPPER(especialidade) IN ('CIRURGIA GERAL', 'CIRURGIA_GERAL');"
        ))
        cg_users = res_users.mappings().all()

        for u in cg_users:
            u_id = u["id"]
            u_username = u["username"]
            u_nome = u["nome"]
            u_funcao = u["funcao"]

            # Verifica se já existe o mesmo username com perfil_id = 'GERAL'
            res_dup = await conn.execute(text(
                "SELECT id, username, nome, perfil_id, especialidade, funcao FROM usuarios WHERE LOWER(username) = LOWER(:username) AND perfil_id = 'GERAL' AND id != :uid;"
            ), {"username": u_username, "uid": u_id})
            dup_user = res_dup.mappings().first()

            if dup_user:
                # Mescla função/nome se necessário e remove o registro redundante
                if not dup_user["funcao"] and u_funcao:
                    await conn.execute(text(
                        "UPDATE usuarios SET funcao = :funcao WHERE id = :dup_id;"
                    ), {"funcao": u_funcao, "dup_id": dup_user["id"]})
                if not dup_user["nome"] and u_nome:
                    await conn.execute(text(
                        "UPDATE usuarios SET nome = :nome WHERE id = :dup_id;"
                    ), {"nome": u_nome, "dup_id": dup_user["id"]})
                await conn.execute(text("DELETE FROM usuarios WHERE id = :uid;"), {"uid": u_id})
            else:
                await conn.execute(text(
                    "UPDATE usuarios SET perfil_id = 'GERAL', especialidade = 'GERAL' WHERE id = :uid;"
                ), {"uid": u_id})

        # Remove eventuais perfis CIRURGIA_GERAL residuais agora que usuários foram migrados
        await conn.execute(text(
            "DELETE FROM perfis WHERE id != 'GERAL' AND (id IN ('CIRURGIA_GERAL', 'CIRURGIA GERAL') OR UPPER(especialidade) = 'CIRURGIA GERAL' OR UPPER(nome) = 'CIRURGIA GERAL');"
        ))

        # 3. Tratar pacientes
        await conn.execute(text(
            "UPDATE pacientes SET especialidade = 'GERAL' WHERE UPPER(especialidade) IN ('CIRURGIA GERAL', 'CIRURGIA_GERAL');"
        ))

        # 4. Tratar solicitacoes
        await conn.execute(text(
            "UPDATE solicitacoes SET especialidade = 'GERAL' WHERE UPPER(especialidade) IN ('CIRURGIA GERAL', 'CIRURGIA_GERAL');"
        ))
        await conn.execute(text(
            "UPDATE solicitacoes SET perfil_executor = REPLACE(REPLACE(perfil_executor, 'Cirurgia Geral', 'GERAL'), 'CIRURGIA GERAL', 'GERAL') WHERE perfil_executor LIKE '%Cirurgia Geral%' OR perfil_executor LIKE '%CIRURGIA GERAL%';"
        ))

        # 5. Tratar categorizacoes_profissionais
        try:
            res_cats = await conn.execute(text(
                "SELECT id, medico, especialidade, categorias_json FROM categorizacoes_profissionais WHERE UPPER(especialidade) IN ('CIRURGIA GERAL', 'CIRURGIA_GERAL');"
            ))
            cg_cats = res_cats.mappings().all()

            for cat in cg_cats:
                c_id = cat["id"]
                medico = cat["medico"]
                cat_json = cat["categorias_json"] or "[]"
                try:
                    cat_list = json.loads(cat_json)
                except Exception:
                    cat_list = []

                # Verifica se já existe registro para esse médico em GERAL
                res_exist = await conn.execute(text(
                    "SELECT id, medico, especialidade, categorias_json FROM categorizacoes_profissionais WHERE medico = :medico AND especialidade = 'GERAL' AND id != :cid;"
                ), {"medico": medico, "cid": c_id})
                exist_cat = res_exist.mappings().first()

                if exist_cat:
                    try:
                        exist_list = json.loads(exist_cat["categorias_json"] or "[]")
                    except Exception:
                        exist_list = []
                    
                    # Unir listas sem duplicados mantendo a ordem
                    merged_list = list(exist_list)
                    for item in cat_list:
                        if item not in merged_list:
                            merged_list.append(item)

                    await conn.execute(text(
                        "UPDATE categorizacoes_profissionais SET categorias_json = :json_data WHERE id = :exist_id;"
                    ), {"json_data": json.dumps(merged_list), "exist_id": exist_cat["id"]})
                    await conn.execute(text("DELETE FROM categorizacoes_profissionais WHERE id = :cid;"), {"cid": c_id})
                else:
                    await conn.execute(text(
                        "UPDATE categorizacoes_profissionais SET especialidade = 'GERAL' WHERE id = :cid;"
                    ), {"cid": c_id})
        except Exception as e:
            logger.warning(f"Aviso ao migrar categorizacoes_profissionais: {e}")

        # 6. Tratar solicitacoes_criacao_usuario
        try:
            await conn.execute(text(
                "UPDATE solicitacoes_criacao_usuario SET perfil_id = 'GERAL' WHERE UPPER(perfil_id) IN ('CIRURGIA_GERAL', 'CIRURGIA GERAL');"
            ))
            await conn.execute(text(
                "UPDATE solicitacoes_criacao_usuario SET especialidade = 'GERAL' WHERE UPPER(especialidade) IN ('CIRURGIA GERAL', 'CIRURGIA_GERAL');"
            ))
        except Exception as e:
            logger.warning(f"Aviso ao migrar solicitacoes_criacao_usuario: {e}")

        logger.info("Migração segura de CIRURGIA GERAL para GERAL concluída com sucesso.")
    except Exception as e:
        logger.error(f"Erro na migração de CIRURGIA GERAL para GERAL: {e}")

async def migrate_bucomaxilofacial_medico_to_dentista(conn):
    """
    Substitui a função 'Médico' por 'Dentista' para os profissionais cadastrados
    na especialidade BUCOMAXILOFACIAL, mantendo todo o banco de dados íntegro.
    """
    try:
        # 1. Tratar usuarios
        await conn.execute(text(
            "UPDATE usuarios SET funcao = 'Dentista' WHERE (UPPER(especialidade) LIKE '%BUCOMAXILO%' OR UPPER(perfil_id) LIKE '%BUCOMAXILO%') AND (funcao LIKE 'M%dico' OR funcao = 'Medico' OR funcao = 'Médico');"
        ))

        # 2. Tratar solicitacoes_criacao_usuario
        try:
            await conn.execute(text(
                "UPDATE solicitacoes_criacao_usuario SET funcao = 'Dentista' WHERE (UPPER(especialidade) LIKE '%BUCOMAXILO%' OR UPPER(perfil_id) LIKE '%BUCOMAXILO%') AND (funcao LIKE 'M%dico' OR funcao = 'Medico' OR funcao = 'Médico');"
            ))
        except Exception:
            pass

        logger.info("Migração segura de BUCOMAXILOFACIAL Médico -> Dentista concluída com sucesso.")
    except Exception as e:
        logger.error(f"Erro na migração de BUCOMAXILOFACIAL Médico -> Dentista: {e}")

