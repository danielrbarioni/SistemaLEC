"""merge_cirurgia_geral_to_geral

Revision ID: e3f4a5b6c7d8
Revises: d2e3f4a5b6c7
Create Date: 2026-09-25 12:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import json

# revision identifiers, used by Alembic.
revision: str = 'e3f4a5b6c7d8'
down_revision: Union[str, Sequence[str], None] = 'd2e3f4a5b6c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Perfis
    res = conn.execute(sa.text("SELECT id, nome, tipo, cor, especialidade FROM perfis WHERE id = 'GERAL';"))
    geral_profile = res.mappings().first()

    res_cg = conn.execute(sa.text(
        "SELECT id, nome, tipo, cor, especialidade FROM perfis WHERE id IN ('CIRURGIA_GERAL', 'CIRURGIA GERAL') OR UPPER(especialidade) = 'CIRURGIA GERAL' OR UPPER(nome) = 'CIRURGIA GERAL';"
    ))
    cg_profiles = res_cg.mappings().all()

    if not geral_profile:
        if cg_profiles:
            first_cg_id = cg_profiles[0]["id"]
            conn.execute(sa.text(
                "UPDATE perfis SET id = 'GERAL', nome = 'GERAL', tipo = 'ESPECIALIDADE', cor = 'verde', especialidade = 'GERAL' WHERE id = :old_id;"
            ), {"old_id": first_cg_id})
        else:
            conn.execute(sa.text(
                "INSERT INTO perfis (id, nome, tipo, cor, especialidade) VALUES ('GERAL', 'GERAL', 'ESPECIALIDADE', 'verde', 'GERAL');"
            ))
    else:
        conn.execute(sa.text(
            "UPDATE perfis SET nome = 'GERAL', tipo = 'ESPECIALIDADE', cor = 'verde', especialidade = 'GERAL' WHERE id = 'GERAL';"
        ))

    # 2. Usuarios
    res_users = conn.execute(sa.text(
        "SELECT id, username, nome, perfil_id, especialidade, funcao FROM usuarios WHERE UPPER(perfil_id) IN ('CIRURGIA_GERAL', 'CIRURGIA GERAL') OR UPPER(especialidade) IN ('CIRURGIA GERAL', 'CIRURGIA_GERAL');"
    ))
    cg_users = res_users.mappings().all()

    for u in cg_users:
        u_id = u["id"]
        u_username = u["username"]
        u_nome = u["nome"]
        u_funcao = u["funcao"]

        res_dup = conn.execute(sa.text(
            "SELECT id, username, nome, perfil_id, especialidade, funcao FROM usuarios WHERE LOWER(username) = LOWER(:username) AND perfil_id = 'GERAL' AND id != :uid;"
        ), {"username": u_username, "uid": u_id})
        dup_user = res_dup.mappings().first()

        if dup_user:
            if not dup_user["funcao"] and u_funcao:
                conn.execute(sa.text(
                    "UPDATE usuarios SET funcao = :funcao WHERE id = :dup_id;"
                ), {"funcao": u_funcao, "dup_id": dup_user["id"]})
            if not dup_user["nome"] and u_nome:
                conn.execute(sa.text(
                    "UPDATE usuarios SET nome = :nome WHERE id = :dup_id;"
                ), {"nome": u_nome, "dup_id": dup_user["id"]})
            conn.execute(sa.text("DELETE FROM usuarios WHERE id = :uid;"), {"uid": u_id})
        else:
            conn.execute(sa.text(
                "UPDATE usuarios SET perfil_id = 'GERAL', especialidade = 'GERAL' WHERE id = :uid;"
            ), {"uid": u_id})

    conn.execute(sa.text(
        "DELETE FROM perfis WHERE id != 'GERAL' AND (id IN ('CIRURGIA_GERAL', 'CIRURGIA GERAL') OR UPPER(especialidade) = 'CIRURGIA GERAL' OR UPPER(nome) = 'CIRURGIA GERAL');"
    ))

    # 3. Pacientes
    conn.execute(sa.text(
        "UPDATE pacientes SET especialidade = 'GERAL' WHERE UPPER(especialidade) IN ('CIRURGIA GERAL', 'CIRURGIA_GERAL');"
    ))

    # 4. Solicitacoes
    conn.execute(sa.text(
        "UPDATE solicitacoes SET especialidade = 'GERAL' WHERE UPPER(especialidade) IN ('CIRURGIA GERAL', 'CIRURGIA_GERAL');"
    ))
    conn.execute(sa.text(
        "UPDATE solicitacoes SET perfil_executor = REPLACE(REPLACE(perfil_executor, 'Cirurgia Geral', 'GERAL'), 'CIRURGIA GERAL', 'GERAL') WHERE perfil_executor LIKE '%Cirurgia Geral%' OR perfil_executor LIKE '%CIRURGIA GERAL%';"
    ))

    # 5. Categorizacoes
    try:
        res_cats = conn.execute(sa.text(
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

            res_exist = conn.execute(sa.text(
                "SELECT id, medico, especialidade, categorias_json FROM categorizacoes_profissionais WHERE medico = :medico AND especialidade = 'GERAL' AND id != :cid;"
            ), {"medico": medico, "cid": c_id})
            exist_cat = res_exist.mappings().first()

            if exist_cat:
                try:
                    exist_list = json.loads(exist_cat["categorias_json"] or "[]")
                except Exception:
                    exist_list = []
                
                merged_list = list(exist_list)
                for item in cat_list:
                    if item not in merged_list:
                        merged_list.append(item)

                conn.execute(sa.text(
                    "UPDATE categorizacoes_profissionais SET categorias_json = :json_data WHERE id = :exist_id;"
                ), {"json_data": json.dumps(merged_list), "exist_id": exist_cat["id"]})
                conn.execute(sa.text("DELETE FROM categorizacoes_profissionais WHERE id = :cid;"), {"cid": c_id})
            else:
                conn.execute(sa.text(
                    "UPDATE categorizacoes_profissionais SET especialidade = 'GERAL' WHERE id = :cid;"
                ), {"cid": c_id})
    except Exception:
        pass

    # 6. Solicitacoes criacao usuario
    try:
        conn.execute(sa.text(
            "UPDATE solicitacoes_criacao_usuario SET perfil_id = 'GERAL' WHERE UPPER(perfil_id) IN ('CIRURGIA_GERAL', 'CIRURGIA GERAL');"
        ))
        conn.execute(sa.text(
            "UPDATE solicitacoes_criacao_usuario SET especialidade = 'GERAL' WHERE UPPER(especialidade) IN ('CIRURGIA GERAL', 'CIRURGIA_GERAL');"
        ))
    except Exception:
        pass


def downgrade() -> None:
    pass
