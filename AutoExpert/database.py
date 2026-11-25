import sqlite3
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
import json

BANCO = Path(__file__).resolve().parent / "autoexpert.db"


def conectar():
    """Abre uma conexão com o banco SQLite."""
    return sqlite3.connect(BANCO)


@contextmanager
def conexao_banco():
    """Gerencia a transação e garante o fechamento da conexão."""
    conexao = conectar()
    try:
        yield conexao
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def criar_tabela():
    """Cria a tabela e atualiza bancos antigos sem apagar os atendimentos."""
    with conexao_banco() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS atendimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora TEXT NOT NULL,
                marca TEXT,
                ano INTEGER,
                placa TEXT,
                quilometragem INTEGER,
                sintomas TEXT,
                diagnostico TEXT,
                confianca REAL,
                urgencia TEXT,
                recomendacao TEXT
            )
        """)
        colunas = {
            linha[1] for linha in conexao.execute(
                "PRAGMA table_info(atendimentos)"
            ).fetchall()
        }
        if "diagnosticos_json" not in colunas:
            conexao.execute(
                "ALTER TABLE atendimentos ADD COLUMN diagnosticos_json TEXT"
            )


def salvar_atendimento(marca, ano, placa, quilometragem, sintomas,
                       diagnostico, confianca, urgencia, recomendacao,
                       diagnosticos=None):
    """
    Salva um atendimento e todos os diagnósticos associados.
    Os campos antigos continuam recebendo o diagnóstico principal
    para manter compatibilidade com registros e chamadas anteriores.
    """
    placa = str(placa or "").strip().upper()
    if not placa:
        raise ValueError("A placa do veículo é obrigatória. O atendimento não foi salvo.")

    lista = diagnosticos or [{
        "nome": diagnostico,
        "confianca": float(confianca or 0),
        "urgencia": urgencia or "Não informada",
        "recomendacao": recomendacao or "",
        "categoria": ""
    }]
    diagnosticos_json = json.dumps(lista, ensure_ascii=False)

    with conexao_banco() as conexao:
        cursor = conexao.execute("""
            INSERT INTO atendimentos (
                data_hora, marca, ano, placa, quilometragem, sintomas,
                diagnostico, confianca, urgencia, recomendacao,
                diagnosticos_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            marca, ano, placa, quilometragem, sintomas,
            diagnostico, confianca, urgencia, recomendacao,
            diagnosticos_json
        ))
        return cursor.lastrowid


def listar_atendimentos(placa=None, limite=100):
    with conexao_banco() as conexao:
        campos = """
            SELECT id, data_hora, marca, ano, placa, quilometragem,
                   sintomas, diagnostico, confianca, urgencia,
                   recomendacao, diagnosticos_json
            FROM atendimentos
        """
        if placa:
            cursor = conexao.execute(
                campos + """
                    WHERE UPPER(placa) = UPPER(?)
                    ORDER BY id DESC
                    LIMIT ?
                """,
                (placa.strip(), limite)
            )
        else:
            cursor = conexao.execute(
                campos + " ORDER BY id DESC LIMIT ?",
                (limite,)
            )
        return cursor.fetchall()


def contar_atendimentos():
    with conexao_banco() as conexao:
        return conexao.execute(
            "SELECT COUNT(*) FROM atendimentos"
        ).fetchone()[0]


def excluir_atendimento(atendimento_id):
    with conexao_banco() as conexao:
        conexao.execute(
            "DELETE FROM atendimentos WHERE id = ?",
            (atendimento_id,)
        )


def listar_todos_atendimentos():
    """Retorna todos os atendimentos para compor os indicadores gerais."""
    with conexao_banco() as conexao:
        return conexao.execute("""
            SELECT id, data_hora, marca, ano, placa, quilometragem,
                   sintomas, diagnostico, confianca, urgencia,
                   recomendacao, diagnosticos_json
            FROM atendimentos
            ORDER BY id DESC
        """).fetchall()
