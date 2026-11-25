import unittest
import tempfile
from pathlib import Path
import database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_banco = database.BANCO
        database.BANCO = Path(self.temp_dir.name) / "teste.db"
        database.criar_tabela()

    def tearDown(self):
        database.BANCO = self.original_banco
        self.temp_dir.cleanup()

    def test_salvar_e_consultar(self):
        registro_id = database.salvar_atendimento(
            "Chevrolet Onix", 2020, "ABC1D23", 50000,
            "motor_nao_liga",
            "Possível bateria descarregada", 0.90,
            "Alta", "Verificar bateria e sistema de partida."
        )
        self.assertEqual(registro_id, 1)

        registros = database.listar_atendimentos("ABC1D23")
        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0][4], "ABC1D23")
        self.assertEqual(registros[0][7], "Possível bateria descarregada")

    def test_excluir(self):
        registro_id = database.salvar_atendimento(
            "Fiat", 2019, "XYZ9A99", 70000,
            "freio_baixo",
            "Possível falha hidráulica", 0.88,
            "Alta", "Encaminhar para inspeção."
        )
        database.excluir_atendimento(registro_id)
        self.assertEqual(database.contar_atendimentos(), 0)


if __name__ == "__main__":
    unittest.main()
