import json
from pathlib import Path

import streamlit as st
import plotly.express as px

from analytics import preparar_indicadores
from relatorios import gerar_relatorio_pdf

#st.title("AutoExpert")
#st.subheader(
#    "Sistema Especialista para Triagem e Diagnóstico Preliminar "
#   "de Falhas Automotivas"
#)

from engine import carregar_regras, inferir
from database import (
    criar_tabela,
    salvar_atendimento,
    listar_atendimentos,
    contar_atendimentos,
    excluir_atendimento,
    listar_todos_atendimentos,
)

st.set_page_config(page_title="AutoExpert", page_icon="🚗", layout="wide")

logo = Path(__file__).resolve().parent / "assets" / "logo_autotech.png"
if logo.exists():
    st.image(str(logo), width=420)


@st.cache_data
def carregar_perguntas():
    caminho = Path(__file__).resolve().parent / "data" / "questions.json"
    return json.loads(caminho.read_text(encoding="utf-8"))


def formatar_km(valor):
    return f"{valor:,}".replace(",", ".")


def limpar_para_novo_atendimento():
    """Limpa os dados do formulário e o resultado exibido, sem apagar o histórico."""
    for chave in st.session_state.get("_ids_sintomas", []):
        st.session_state[chave] = False

    st.session_state["marca_veiculo"] = ""
    st.session_state["ano_veiculo"] = 2020
    st.session_state["placa_veiculo"] = ""
    st.session_state["km_veiculo"] = 50000

    for chave in ("resultado", "veiculo", "fatos", "registro_id"):
        st.session_state.pop(chave, None)
    st.session_state["novo_atendimento_iniciado"] = True


def salvar_resultado_no_historico(veiculo, fatos, resultado):
    if not resultado["resultados"]:
        return None

    # Converte todos os resultados do motor para uma estrutura serializável.
    # O histórico passa a guardar todos os diagnósticos do mesmo atendimento.
    diagnosticos = [
        {
            "nome": item.nome,
            "categoria": item.categoria,
            "confianca": float(item.confianca),
            "urgencia": item.urgencia,
            "recomendacao": item.recomendacao,
        }
        for item in resultado["resultados"]
    ]

    principal = diagnosticos[0]
    sintomas = ", ".join(sorted(fatos)) if fatos else "Nenhum sintoma informado"

    return salvar_atendimento(
        marca=veiculo["marca"],
        ano=veiculo["ano"],
        placa=veiculo["placa"],
        quilometragem=veiculo["km"],
        sintomas=sintomas,
        diagnostico=principal["nome"],
        confianca=principal["confianca"],
        urgencia=principal["urgencia"],
        recomendacao=principal["recomendacao"],
        diagnosticos=diagnosticos,
    )


regras = carregar_regras()
perguntas = carregar_perguntas()
criar_tabela()

# Guarda os identificadores para que o botão de limpeza possa desmarcar
# todos os sintomas selecionados no atendimento anterior.
st.session_state["_ids_sintomas"] = [q["id"] for q in perguntas]

st.title("AutoExpert")
st.subheader("Sistema Especialista para Triagem e Diagnóstico Preliminar de Falhas Automotivas")
st.info(
    "o resultado é uma triagem preliminar e não substitui "
    "o diagnóstico de um profissional."
)

# Menu principal em abas: diagnóstico e histórico.
aba_diagnostico, aba_historico, aba_indicadores = st.tabs(["🔎 Novo diagnóstico", "📋 Histórico de atendimentos", "📊 Indicadores"])

with aba_diagnostico:
    topo_novo, _ = st.columns([1, 4])
    with topo_novo:
        st.button(
            "➕ Novo diagnóstico",
            help="Inicia um novo atendimento, desmarcando os sintomas e limpando os dados e o resultado anterior. O histórico será preservado.",
            on_click=limpar_para_novo_atendimento,
            width="stretch",
        )
    if st.session_state.pop("novo_atendimento_iniciado", False):
        st.success("Novo atendimento iniciado. Informe os dados do veículo e selecione os sintomas.")

    with st.sidebar:
        st.header("Dados do veículo")
        st.session_state.setdefault("marca_veiculo", "")
        st.session_state.setdefault("ano_veiculo", 2020)
        st.session_state.setdefault("placa_veiculo", "")
        st.session_state.setdefault("km_veiculo", 50000)
        marca = st.text_input(
            "Marca/modelo", placeholder="Ex.: Chevrolet Onix", key="marca_veiculo"
        )
        ano = st.number_input(
            "Ano", min_value=1950, max_value=2030, step=1, key="ano_veiculo"
        )
        placa = st.text_input(
            "Placa (obrigatória)",
            key="placa_veiculo",
            placeholder="Ex.: ABC1D23",
            help="Informe a placa para liberar o diagnóstico.",
        ).strip().upper()
        km = st.number_input(
            "Quilometragem", min_value=0, max_value=9999999,
            step=1000, key="km_veiculo"
        )

    st.markdown("### 1. Informe os sintomas")
    st.caption("Marque somente os sintomas observados. As perguntas estão agrupadas por categoria.")

    respostas = {}
    for categoria in dict.fromkeys(q["categoria"] for q in perguntas):
        with st.expander(categoria, expanded=True):
            cols = st.columns(2)
            itens = [q for q in perguntas if q["categoria"] == categoria]
            for i, q in enumerate(itens):
                respostas[q["id"]] = cols[i % 2].checkbox(q["texto"], key=q["id"])

    fatos = {k for k, v in respostas.items() if v}

    st.divider()
    executar_diagnostico = st.button(
        "🔎 Executar diagnóstico", type="primary", width="stretch"
    )

    if executar_diagnostico:
        if not placa:
            st.error("A placa do veículo é obrigatória. Informe a placa antes de executar o diagnóstico.")
            st.stop()

        if not fatos:
            st.warning("Nenhum sintoma foi selecionado. O resultado será inconclusivo.")

        resultado = inferir(fatos, regras)
        veiculo = {
            "marca": marca or "Não informado",
            "ano": ano,
            "placa": placa,
            "km": km,
        }

        st.session_state["resultado"] = resultado
        st.session_state["veiculo"] = veiculo
        st.session_state["fatos"] = fatos

        # Persistência: o atendimento é gravado automaticamente.
        registro_id = salvar_resultado_no_historico(veiculo, fatos, resultado)
        st.session_state["registro_id"] = registro_id

    if "resultado" in st.session_state:
        r = st.session_state["resultado"]
        v = st.session_state["veiculo"]
        fatos_resultado = st.session_state.get("fatos", set())

        st.header("2. Resultado da triagem")
        st.write(
            f"**Veículo:** {v['marca']} | **Ano:** {v['ano']} | "
            f"**Placa:** {v['placa']} | **Km:** {formatar_km(v['km'])}"
        )

        registro_id = st.session_state.get("registro_id")
        if registro_id:
            st.success(f"Atendimento #{registro_id} salvo no histórico.")

        top = r["resultados"][0]
        if top.conclusao == "inconclusivo":
            st.warning(
                "### Resultado inconclusivo\n"
                "Não foram encontrados fatos suficientes para uma conclusão específica."
            )
            st.write("**Recomendação:**", top.recomendacao)
        else:
            for i, x in enumerate(r["resultados"][:5], 1):
                with st.container(border=True):
                    c1, c2, c3 = st.columns([4, 1, 1])
                    c1.markdown(f"**{i}. {x.nome}**")
                    c2.metric("Confiança", f"{x.confianca:.0%}")
                    c3.metric("Urgência", x.urgencia)
                    st.write("**Categoria:**", x.categoria)
                    st.write("**Recomendação:**", x.recomendacao)

        st.header("3. Explicação do raciocínio")
        st.caption("Regras que foram satisfeitas pelo conjunto de fatos informado:")
        if r["regras_disparadas"]:
            for x in r["regras_disparadas"]:
                with st.expander(f"{x.id} — {x.nome}"):
                    if x.condicoes:
                        st.write("**Condições:**", ", ".join(x.condicoes))
                    st.write("**Conclusão produzida:**", x.conclusao)
                    st.write("**Explicação:**", x.explicacao)
        else:
            st.write("Nenhuma regra específica foi acionada.")

        st.header("4. Fatos utilizados")
        st.write(", ".join(sorted(fatos_resultado)) if fatos_resultado else "Nenhum fato positivo.")

with aba_historico:
    st.header("📋 Histórico de atendimentos")
    st.caption(
        "Os registros ficam armazenados no banco SQLite local "
        "`autoexpert.db` dentro da pasta do projeto."
    )

    total = contar_atendimentos()
    st.metric("Atendimentos armazenados", total)

    busca_placa = st.text_input(
        "Consultar por placa",
        placeholder="Ex.: ABC1D23",
        key="busca_placa",
    ).strip().upper()

    registros = listar_atendimentos(placa=busca_placa or None, limite=100)

    if not registros:
        st.info("Nenhum atendimento encontrado.")
    else:
        for registro in registros:
            (
                atendimento_id,
                data_hora,
                marca_modelo,
                ano_registro,
                placa_registro,
                quilometragem,
                sintomas,
                diagnostico,
                confianca,
                urgencia,
                recomendacao,
                diagnosticos_json,
            ) = registro

            titulo = (
                f"Atendimento #{atendimento_id} — {marca_modelo} — "
                f"{placa_registro} — {data_hora}"
            )
            with st.expander(titulo):
                st.write(f"**Ano:** {ano_registro}")
                st.write(f"**Quilometragem:** {formatar_km(quilometragem)} km")
                st.write("**Sintomas/fatos:**", sintomas)

                # Registros antigos não possuem a coluna JSON preenchida.
                if diagnosticos_json:
                    try:
                        diagnosticos_atendimento = json.loads(diagnosticos_json)
                    except (TypeError, json.JSONDecodeError):
                        diagnosticos_atendimento = []
                else:
                    diagnosticos_atendimento = []

                if not diagnosticos_atendimento:
                    diagnosticos_atendimento = [{
                        "nome": diagnostico,
                        "confianca": confianca or 0,
                        "urgencia": urgencia or "Não informada",
                        "recomendacao": recomendacao or "",
                        "categoria": "",
                    }]

                st.markdown(f"**Diagnósticos registrados: {len(diagnosticos_atendimento)}**")
                for indice, item in enumerate(diagnosticos_atendimento, 1):
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([4, 1, 1])
                        c1.markdown(f"**{indice}. {item.get('nome', 'Não informado')}**")
                        c2.metric("Confiança", f"{float(item.get('confianca', 0)):.0%}")
                        c3.metric("Urgência", item.get("urgencia", "Não informada"))
                        if item.get("categoria"):
                            st.write("**Categoria:**", item["categoria"])
                        st.write("**Recomendação:**", item.get("recomendacao", ""))

                pdf = gerar_relatorio_pdf(registro)
                st.download_button(
                    "📄 Gerar relatório PDF",
                    data=pdf,
                    file_name=f"AutoExpert_atendimento_{atendimento_id}.pdf",
                    mime="application/pdf",
                    key=f"pdf_{atendimento_id}",
                    width="stretch",
                )

                if st.button(
                    "🗑️ Excluir este atendimento",
                    key=f"excluir_{atendimento_id}",
                ):
                    excluir_atendimento(atendimento_id)
                    st.success("Atendimento excluído.")
                    st.rerun()


with aba_indicadores:
    st.header("📊 Indicadores dos atendimentos")
    st.caption("Estatísticas calculadas a partir dos atendimentos armazenados no SQLite.")
    todos_registros = listar_todos_atendimentos()
    if not todos_registros:
        st.info("Ainda não existem atendimentos registrados para gerar indicadores.")
    else:
        dados = preparar_indicadores(todos_registros)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de atendimentos", len(todos_registros))
        c2.metric("Diagnósticos distintos", len(dados["diagnosticos"]))
        c3.metric("Categorias identificadas", len(dados["categorias"]))

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Atendimentos por categoria")
            if dados["categorias"]:
                fig = px.bar(x=list(dados["categorias"].keys()), y=list(dados["categorias"].values()), labels={"x": "Categoria", "y": "Ocorrências"}, title="Categorias de falhas")
                fig.update_layout(xaxis_tickangle=-25)
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("Não há categorias disponíveis.")
        with col2:
            st.subheader("Diagnósticos mais frequentes")
            if dados["diagnosticos"]:
                frequentes = sorted(dados["diagnosticos"].items(), key=lambda item: item[1], reverse=True)[:10]
                fig = px.bar(x=[x[0] for x in frequentes], y=[x[1] for x in frequentes], labels={"x": "Diagnóstico", "y": "Ocorrências"}, title="Até 10 diagnósticos mais frequentes")
                fig.update_layout(xaxis_tickangle=-25)
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("Não há diagnósticos disponíveis.")

        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Atendimentos por mês")
            if dados["por_mes"]:
                fig = px.line(x=list(dados["por_mes"].keys()), y=list(dados["por_mes"].values()), markers=True, labels={"x": "Mês", "y": "Atendimentos"}, title="Evolução mensal")
                st.plotly_chart(fig, width="stretch")
        with col4:
            st.subheader("Distribuição por urgência")
            if dados["urgencias"]:
                fig = px.pie(names=list(dados["urgencias"].keys()), values=list(dados["urgencias"].values()), title="Urgência dos diagnósticos")
                st.plotly_chart(fig, width="stretch")

        st.caption("Observação: as contagens consideram cada categoria, diagnóstico ou urgência uma vez por atendimento. Os gráficos refletem apenas os registros disponíveis no banco de dados.")
