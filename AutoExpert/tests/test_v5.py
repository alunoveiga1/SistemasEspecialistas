import json
import unittest
from analytics import preparar_indicadores, extrair_diagnosticos
from relatorios import gerar_relatorio_pdf


class TestV5(unittest.TestCase):
    def setUp(self):
        self.registro = (
            7, "17/11/2026 10:30:00", "Chevrolet Onix", 2020, "ABC1D23",
            50000, "nao_liga, motor_nao_gira", "Bateria descarregada", 0.94,
            "Alta", "Testar bateria", json.dumps([
                {"nome": "Bateria descarregada", "categoria": "Partida e bateria", "confianca": 0.94, "urgencia": "Alta", "recomendacao": "Testar bateria"},
                {"nome": "Falha no motor de partida", "categoria": "Partida e bateria", "confianca": 0.90, "urgencia": "Média", "recomendacao": "Inspecionar motor de partida"},
            ], ensure_ascii=False)
        )

    def test_indicadores_contam_atendimento_e_diagnosticos(self):
        dados = preparar_indicadores([self.registro])
        self.assertEqual(dados["categorias"]["Partida e bateria"], 1)
        self.assertEqual(dados["diagnosticos"]["Bateria descarregada"], 1)
        self.assertEqual(dados["por_mes"]["2026-11"], 1)

    def test_compatibilidade_com_registro_antigo(self):
        antigo = self.registro[:11] + (None,)
        itens = extrair_diagnosticos(antigo)
        self.assertEqual(len(itens), 1)
        self.assertEqual(itens[0]["nome"], "Bateria descarregada")

    def test_geracao_pdf(self):
        pdf = gerar_relatorio_pdf(self.registro)
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertGreater(len(pdf), 1000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
