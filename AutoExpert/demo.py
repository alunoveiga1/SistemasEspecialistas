from engine import carregar_regras, inferir
regras=carregar_regras()
caso={"falha_motor","perda_potencia","luz_injecao"}
resultado=inferir(caso,regras)
print("Diagnóstico:",resultado["resultados"][0].nome)
print("Confiança:",resultado["resultados"][0].confianca)
print("Regras:",[r.id for r in resultado["regras_disparadas"]])
