import json
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Regra:
    id:str; nome:str; categoria:str; condicoes:list; conclusao:str; tipo:str
    confianca:float; urgencia:str; recomendacao:str; explicacao:str

def carregar_regras(caminho="data/rules.json"):
    dados=json.loads(Path(caminho).read_text(encoding="utf-8"))
    return [Regra(**x) for x in dados]

def inferir(fatos, regras):
    fatos=set(fatos); disparadas=[]; diagnosticos=[]; ids=set(); mudou=True
    while mudou:
        mudou=False
        for r in regras:
            if r.tipo=="fallback" or r.id in ids:
                continue
            if all(c in fatos for c in r.condicoes):
                ids.add(r.id); disparadas.append(r)
                if r.conclusao not in fatos:
                    fatos.add(r.conclusao); mudou=True
                if r.tipo=="diagnostico":
                    diagnosticos.append(r)
    melhores={}
    for r in diagnosticos:
        if r.conclusao not in melhores or r.confianca>melhores[r.conclusao].confianca:
            melhores[r.conclusao]=r
    if not melhores:
        fallback=next(r for r in regras if r.tipo=="fallback")
        resultados=[fallback]
    else:
        resultados=sorted(melhores.values(),key=lambda x:x.confianca,reverse=True)
    return {"fatos_finais":fatos,"regras_disparadas":disparadas,"resultados":resultados}
