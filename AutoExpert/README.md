# AutoExpert V5 — AutoTech Serviços Automotivos

Sistema especialista acadêmico para triagem e diagnóstico preliminar de falhas automotivas. A V5 preserva a base de conhecimento com 36 regras, o motor Forward Chaining, a interface Streamlit e o histórico SQLite da V4, acrescentando painel de indicadores com Plotly e relatórios individuais em PDF com ReportLab.

## Funcionalidades
- Cadastro de dados do veículo e seleção de sintomas.
- Inferência por Forward Chaining usando `data/rules.json`.
- Apresentação de múltiplos diagnósticos, confiança, urgência e recomendações.
- Explicação das regras acionadas e dos fatos utilizados.
- Salvamento automático dos atendimentos no SQLite, preservando múltiplos diagnósticos.
- Consulta do histórico geral e por placa, detalhes e exclusão de registros.
- Botão Novo diagnóstico, sem apagar o histórico.
- Painel Plotly: atendimentos por categoria, diagnósticos frequentes, evolução mensal e urgência.
- Download de relatório PDF por atendimento, com todos os diagnósticos registrados.

## Requisitos
Python 3.10 ou superior recomendado.

## Instalação (Windows / VS Code)
Abra a pasta do projeto no VS Code e execute no terminal:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

A aplicação normalmente abre em `http://localhost:8501`.

## Testes automatizados
Na pasta raiz do projeto:

```powershell
python -m unittest discover -s tests -v
```

Os testes cobrem o motor de inferência, operações de banco, múltiplos diagnósticos, preparação dos indicadores e geração de PDF.

## Estrutura
- `app.py`: interface Streamlit.
- `engine.py`: motor Forward Chaining.
- `database.py`: persistência SQLite e consultas.
- `analytics.py`: preparação de dados para indicadores.
- `relatorios.py`: geração de relatórios PDF.
- `data/questions.json`: perguntas e sintomas.
- `data/rules.json`: 36 regras da base de conhecimento.
- `assets/logo_autotech.png`: logotipo.
- `tests/`: testes automatizados.

## Banco de dados e atualização da V4
O banco `autoexpert.db` é criado automaticamente. A V5 utiliza a mesma estrutura de atendimentos da V4 e mantém compatibilidade com registros anteriores, incluindo atendimentos sem `diagnosticos_json`. **Ao atualizar uma instalação existente, preserve o arquivo `autoexpert.db`; não o apague.**

## Observação
O AutoExpert é uma ferramenta acadêmica de apoio à decisão. Os resultados são hipóteses baseadas nos sintomas informados e nas regras cadastradas; não substituem inspeção nem diagnóstico de profissional qualificado.
