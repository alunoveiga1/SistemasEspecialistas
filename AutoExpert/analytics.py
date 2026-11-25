"""Preparação de indicadores a partir dos atendimentos armazenados."""
import json
from collections import Counter
from datetime import datetime


def extrair_diagnosticos(registro):
    """Aceita a tupla retornada por listar_atendimentos e preserva registros antigos."""
    diagnostico = registro[7]
    confianca = registro[8]
    urgencia = registro[9]
    recomendacao = registro[10]
    diagnosticos_json = registro[11] if len(registro) > 11 else None
    try:
        itens = json.loads(diagnosticos_json) if diagnosticos_json else []
    except (TypeError, json.JSONDecodeError):
        itens = []
    if not itens:
        itens = [{
            "nome": diagnostico or "Não informado",
            "categoria": "Não categorizado",
            "confianca": confianca or 0,
            "urgencia": urgencia or "Não informada",
            "recomendacao": recomendacao or "",
        }]
    return itens


def preparar_indicadores(registros):
    """Retorna contagens para gráficos; conta cada atendimento uma vez por categoria/diagnóstico."""
    categorias = Counter()
    diagnosticos = Counter()
    por_mes = Counter()
    urgencias = Counter()
    for registro in registros:
        data_hora = registro[1] or ""
        try:
            data = datetime.strptime(data_hora, "%d/%m/%Y %H:%M:%S")
            por_mes[data.strftime("%Y-%m")] += 1
        except ValueError:
            por_mes["Data não identificada"] += 1
        itens = extrair_diagnosticos(registro)
        categorias_atendimento = set()
        diagnosticos_atendimento = set()
        urgencias_atendimento = set()
        for item in itens:
            nome = item.get("nome") or "Não informado"
            categoria = item.get("categoria") or "Não categorizado"
            urgencia = item.get("urgencia") or "Não informada"
            diagnosticos_atendimento.add(nome)
            categorias_atendimento.add(categoria)
            urgencias_atendimento.add(urgencia)
        diagnosticos.update(diagnosticos_atendimento)
        categorias.update(categorias_atendimento)
        urgencias.update(urgencias_atendimento)
    return {
        "categorias": dict(categorias),
        "diagnosticos": dict(diagnosticos),
        "por_mes": dict(sorted(por_mes.items())),
        "urgencias": dict(urgencias),
    }
