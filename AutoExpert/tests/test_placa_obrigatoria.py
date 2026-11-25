import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import database


class TestPlacaObrigatoria(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "teste.db"
        self.patch_banco = patch.object(database, "BANCO", self.db_path)
        self.patch_banco.start()
        database.criar_tabela()

    def tearDown(self):
        self.patch_banco.stop()
        self.temp_dir.cleanup()

    def salvar(self, placa):
        return database.salvar_atendimento(
            marca="Chevrolet Onix", ano=2020, placa=placa,
            quilometragem=50000, sintomas="motor_nao_liga",
            diagnostico="Falha na partida", confianca=0.9,
            urgencia="Média", recomendacao="Inspecionar sistema de partida"
        )

    def test_bloqueia_placa_vazia(self):
        with self.assertRaisesRegex(ValueError, "placa.*obrigatória"):
            self.salvar("")
        self.assertEqual(database.contar_atendimentos(), 0)

    def test_bloqueia_placa_apenas_com_espacos(self):
        with self.assertRaises(ValueError):
            self.salvar("   ")
        self.assertEqual(database.contar_atendimentos(), 0)

    def test_salva_placa_em_maiusculas(self):
        registro_id = self.salvar("abc1d23")
        self.assertEqual(registro_id, 1)
        self.assertEqual(database.listar_atendimentos()[0][4], "ABC1D23")


if __name__ == "__main__":
    unittest.main(verbosity=2)
