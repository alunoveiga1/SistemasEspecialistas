# AutoExpert V5 — resumo técnico

A V5 preserva as funcionalidades da V4 e acrescenta indicadores com Plotly e relatórios PDF com ReportLab.

## Novos módulos
- `analytics.py`: consolida os atendimentos do SQLite para os gráficos.
- `relatorios.py`: gera PDF individual com dados do veículo, sintomas e todos os diagnósticos do atendimento.

## Novas áreas da interface
- **Indicadores:** total de atendimentos, categorias, diagnósticos frequentes, evolução mensal e urgência.
- **Histórico:** botão para gerar o relatório PDF de cada atendimento.

## Dependências adicionais
- `plotly`
- `reportlab`

Consulte `AutoExpert_V5_Documentacao_Tecnica.docx` e `../README.md` para a documentação completa e instruções de execução.
