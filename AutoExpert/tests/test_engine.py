import sys, unittest
sys.path.insert(0,".")
from engine import carregar_regras,inferir

class TestAutoExpert(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.regras=carregar_regras()
    def test_minimo_20_regras(self): self.assertGreaterEqual(len(self.regras),20)
    def test_bateria(self):
        r=inferir({"nao_liga","motor_nao_gira","bateria_fraca"},self.regras)
        self.assertEqual(r["resultados"][0].conclusao,"bateria_descarregada")
    def test_superaquecimento(self):
        r=inferir({"temperatura_alta","superaquecimento"},self.regras)
        self.assertEqual(r["resultados"][0].urgencia,"Crítica")
    def test_forward_chaining(self):
        r=inferir({"falha_motor","perda_potencia","luz_injecao"},self.regras)
        ids=[x.id for x in r["regras_disparadas"]]
        self.assertIn("R31",ids); self.assertIn("R32",ids)
    def test_inconclusivo(self):
        r=inferir(set(),self.regras)
        self.assertEqual(r["resultados"][0].conclusao,"inconclusivo")

if __name__=="__main__": unittest.main(verbosity=2)
