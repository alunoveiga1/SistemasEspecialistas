import json
import tempfile
import unittest
from pathlib import Path
import database


class TestMultiplosDiagnosticos(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.original = database.BANCO
        database.BANCO = Path(self.temp.name) / "teste.db"
        database.criar_tabela()

    def tearDown(self):
        database.BANCO = self.original
        self.temp.cleanup()

    def test_salva_e_lista_varios_diagnosticos(self):
        itens = [
            {"nome": "Bateria descarregada", "categoria": "Elétrica",
             "confianca": 0.94, "urgencia": "Alta",
             "recomendacao": "Testar bateria."},
            {"nome": "Falha no alternador", "categoria": "Elétrica",
             "confianca": 0.82, "urgencia": "Média",
             "recomendacao": "Verificar carga."}
        ]
        database.salvar_atendimento(
            "Chevrolet Onix", 2020, "ABC1D23", 50000,
            "motor_nao_liga", itens[0]["nome"], itens[0]["confianca"],
            itens[0]["urgencia"], itens[0]["recomendacao"],
            diagnosticos=itens
        )
        registro = database.listar_atendimentos("ABC1D23")[0]
        recuperados = json.loads(registro[11])
        self.assertEqual(len(recuperados), 2)
        self.assertEqual(recuperados[1]["nome"], "Falha no alternador")

    def test_chamada_antiga_continua_funcionando(self):
        database.salvar_atendimento(
            "Fiat", 2019, "XYZ9A99", 70000, "freio_baixo",
            "Falha hidráulica", 0.88, "Alta", "Inspecionar freios."
        )
        registro = database.listar_atendimentos()[0]
        recuperados = json.loads(registro[11])
        self.assertEqual(len(recuperados), 1)
        self.assertEqual(recuperados[0]["nome"], "Falha hidráulica")

    def test_migra_tabela_antiga_sem_apagar_registros(self):
        # Simula um banco V4 antigo, sem a coluna diagnosticos_json.
        database.BANCO = Path(self.temp.name) / "antigo.db"
        with database.conexao_banco() as con:
            con.execute("""
                CREATE TABLE atendimentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_hora TEXT NOT NULL, marca TEXT, ano INTEGER,
                    placa TEXT, quilometragem INTEGER, sintomas TEXT,
                    diagnostico TEXT, confianca REAL, urgencia TEXT,
                    recomendacao TEXT
                )
            """)
            con.execute("""
                INSERT INTO atendimentos
                (data_hora, marca, ano, placa, quilometragem, sintomas,
                 diagnostico, confianca, urgencia, recomendacao)
                VALUES ('01/01/2026 10:00:00', 'Ford', 2020, 'OLD1A11',
                        40000, 'falha', 'Diagnóstico antigo', 0.8,
                        'Média', 'Verificar')
            """)
        database.criar_tabela()
        registro = database.listar_atendimentos("OLD1A11")[0]
        self.assertEqual(registro[7], "Diagnóstico antigo")
        self.assertIsNone(registro[11])


if __name__ == "__main__":
    unittest.main()
