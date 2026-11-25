"""Geração de relatório PDF individual de atendimento."""
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether


def gerar_relatorio_pdf(registro):
    """Recebe uma tupla de listar_atendimentos e devolve os bytes do PDF."""
    (atendimento_id, data_hora, marca, ano, placa, km, sintomas,
     diagnostico, confianca, urgencia, recomendacao, diagnosticos_json) = registro
    import json
    try:
        diagnosticos = json.loads(diagnosticos_json) if diagnosticos_json else []
    except (TypeError, json.JSONDecodeError):
        diagnosticos = []
    if not diagnosticos:
        diagnosticos = [{
            "nome": diagnostico or "Não informado", "categoria": "Não categorizado",
            "confianca": confianca or 0, "urgencia": urgencia or "Não informada",
            "recomendacao": recomendacao or "",
        }]

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
        topMargin=16*mm, bottomMargin=16*mm,
        title=f"AutoExpert - Atendimento {atendimento_id}",
        author="AutoTech Serviços Automotivos",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#17365D"), fontSize=18, leading=22))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], textColor=colors.HexColor("#17365D"), spaceBefore=10, spaceAfter=6))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8, leading=11))
    story = [
        Paragraph("AutoTech Serviços Automotivos", styles["ReportTitle"]),
        Paragraph("Relatório de triagem e diagnóstico preliminar", styles["Heading2"]),
        Paragraph(f"Atendimento #{atendimento_id} &nbsp; | &nbsp; Data: {escape(str(data_hora or 'Não informada'))}", styles["BodyText"]),
        Spacer(1, 8),
        Paragraph("1. Dados do veículo", styles["Section"]),
    ]
    dados = [
        ["Marca/modelo", str(marca or "Não informado"), "Ano", str(ano or "Não informado")],
        ["Placa", str(placa or "Não informada"), "Quilometragem", f"{km:,} km" if isinstance(km, (int, float)) else str(km or "Não informada")],
    ]
    tabela = Table(dados, colWidths=[27*mm, 62*mm, 25*mm, 48*mm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#EAF0F6")),
        ("BACKGROUND", (2,0), (2,-1), colors.HexColor("#EAF0F6")),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#B7C5D3")),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]))
    story += [tabela, Paragraph("2. Sintomas informados", styles["Section"]), Paragraph(escape(str(sintomas or "Não informado")), styles["BodyText"]), Paragraph("3. Diagnósticos identificados", styles["Section"])]
    for i, item in enumerate(diagnosticos, 1):
        nome = escape(str(item.get("nome", "Não informado")))
        categoria = escape(str(item.get("categoria") or "Não categorizado"))
        urg = escape(str(item.get("urgencia") or "Não informada"))
        rec = escape(str(item.get("recomendacao") or "Não informada"))
        try:
            conf = float(item.get("confianca", 0))
            conf_txt = f"{conf:.0%}" if conf <= 1 else f"{conf:.1f}%"
        except (TypeError, ValueError):
            conf_txt = "Não informada"
        story.append(KeepTogether([
            Paragraph(f"<b>{i}. {nome}</b>", styles["BodyText"]),
            Paragraph(f"Categoria: {categoria} | Confiança: {conf_txt} | Urgência: {urg}", styles["Small"]),
            Paragraph(f"Recomendação: {rec}", styles["BodyText"]),
            Spacer(1, 6),
        ]))
    story += [
        Paragraph("Observação importante", styles["Section"]),
        Paragraph("Este documento apresenta hipóteses de triagem produzidas pelo AutoExpert com base nos sintomas informados e nas regras cadastradas. Não representa confirmação de defeito nem substitui inspeção, diagnóstico ou reparo por profissional qualificado.", styles["Small"]),
        Spacer(1, 10),
        Paragraph("AutoTech Serviços Automotivos — AutoExpert", styles["Small"]),
    ]
    doc.build(story)
    return buffer.getvalue()
