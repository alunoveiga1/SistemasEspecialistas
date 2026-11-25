# Como executar o AutoExpert V5

1. Faça uma cópia de segurança da pasta atual do AutoExpert V4.
2. Extraia o pacote V5 em uma pasta nova.
3. Se deseja manter o histórico, copie o arquivo `autoexpert.db` da V4 para a raiz da pasta V5. Não apague o banco original.
4. Abra a pasta V5 no VS Code.
5. No terminal, execute `python -m pip install -r requirements.txt`.
6. Execute `python -m streamlit run app.py`.
7. Abra `http://localhost:8501` no navegador, se ele não abrir automaticamente.

Na aba Histórico, abra um atendimento e clique em **Gerar relatório PDF**. Na aba Indicadores, consulte os gráficos construídos a partir dos registros do banco.

Para testar: `python -m unittest discover -s tests -v`.
