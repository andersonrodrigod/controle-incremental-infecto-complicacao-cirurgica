import logging

import pandas as pd

from core.caminhos import obter_caminho_arquivo, obter_caminho_pasta
from core.config import carregar_configuracoes
from services.backup import criar_backup_arquivo, gerar_timestamp_backup
from services.historico import identificar_registros_novos
from services.leitura import ler_excel
from services.processamento import (
    filtrar_registros_p1,
    filtrar_registros_rp1,
    restaurar_nomes_tecnicos,
    selecionar_colunas_destino
)
from services.validacao import (
    validar_colunas_obrigatorias,
    validar_dataframe_vazio
)
from services.escrita import salvar_excel


logger = logging.getLogger(__name__)


def executar_pipeline() -> None:
    logger.info("Iniciando execucao do pipeline...")

    # 1. Carregamento das configurações
    configuracoes = carregar_configuracoes()

    configuracao_entrada = configuracoes["arquivos"]["entrada"]
    configuracao_destino_p1 = configuracoes["arquivos"]["destino_p1"]
    configuracao_destino_rp1 = configuracoes["arquivos"]["destino_rp1"]

    regras_processamento = configuracoes[
        "regras_processamento"
    ]

    # 2. Montagem dos caminhos
    caminho_entrada = obter_caminho_arquivo("entrada")
    caminho_destino_p1 = obter_caminho_arquivo("destino_p1")
    caminho_destino_rp1 = obter_caminho_arquivo("destino_rp1")
    caminho_backups = obter_caminho_pasta("backups")

    # 3. Leitura da entrada
    dados = ler_excel(
        caminho_arquivo=caminho_entrada,
        nome_aba=configuracao_entrada["aba"]
    )

    # 4. Validações da entrada
    validar_dataframe_vazio(dados)

    validar_colunas_obrigatorias(
        dados=dados,
        colunas_obrigatorias=configuracoes[
            "colunas_obrigatorias"
        ]
    )

    # 5. Regras configuradas
    regra_p1 = regras_processamento["p1"]
    regra_rp1 = regras_processamento["rp1"]

    # 6. Processamento do P1
    dados_p1 = filtrar_registros_p1(
        dados=dados,
        coluna=regra_p1["coluna"],
        valores_aceitos=regra_p1["valores_aceitos"]
    )

    dados_p1 = selecionar_colunas_destino(
        dados=dados_p1,
        colunas_destino=configuracoes[
            "colunas_destino"
        ]["p1"]
    )

    # 7. Processamento do RP1
    dados_rp1 = filtrar_registros_rp1(
        dados=dados,
        coluna=regra_rp1["coluna"],
        valor_minimo=regra_rp1["valor_minimo"],
        valor_maximo=regra_rp1["valor_maximo"]
    )

    dados_rp1 = selecionar_colunas_destino(
        dados=dados_rp1,
        colunas_destino=configuracoes[
            "colunas_destino"
        ]["rp1"]
    )

    # 8. Leitura do histórico P1
    if caminho_destino_p1.exists():
        historico_p1 = ler_excel(
            caminho_arquivo=caminho_destino_p1,
            nome_aba=configuracao_destino_p1["aba"]
        )

        historico_p1 = restaurar_nomes_tecnicos(
            dados=historico_p1,
            mapa_renomeacao=configuracoes[
                "renomear_colunas"
            ]["p1"]
        )

    else:
        historico_p1 = pd.DataFrame()

    # 9. Leitura do histórico RP1
    if caminho_destino_rp1.exists():
        historico_rp1 = ler_excel(
            caminho_arquivo=caminho_destino_rp1,
            nome_aba=configuracao_destino_rp1["aba"]
        )

        historico_rp1 = restaurar_nomes_tecnicos(
            dados=historico_rp1,
            mapa_renomeacao=configuracoes[
                "renomear_colunas"
            ]["rp1"]
        )

    else:
        historico_rp1 = pd.DataFrame()

    # 10. Identificação dos registros novos
    novos_p1 = identificar_registros_novos(
        dados_atuais=dados_p1,
        dados_historico=historico_p1,
        coluna_chave="SENHA"
    )

    novos_rp1 = identificar_registros_novos(
        dados_atuais=dados_rp1,
        dados_historico=historico_rp1,
        coluna_chave="SENHA"
    )

    # 11. Resumo da execução
    logger.info("Arquivo lido: %s", caminho_entrada.name)
    logger.info("Aba lida: %s", configuracao_entrada["aba"])
    logger.info("Linhas lidas: %s", dados.shape[0])
    logger.info("Colunas lidas: %s", dados.shape[1])

    logger.info(
        "Registros selecionados para P1: %s",
        dados_p1.shape[0]
    )

    logger.info(
        "Novos registros para P1: %s",
        novos_p1.shape[0]
    )

    logger.info(
        "Registros selecionados para RP1: %s",
        dados_rp1.shape[0]
    )

    logger.info(
        "Novos registros para RP1: %s",
        novos_rp1.shape[0]
    )

    dados_finais_p1 = pd.concat(
        [historico_p1, novos_p1],
        ignore_index=True
    )

    dados_finais_rp1 = pd.concat(
        [historico_rp1, novos_rp1],
        ignore_index=True
    )

    dados_finais_p1 = dados_finais_p1.rename(
        columns=configuracoes["renomear_colunas"]["p1"]
    )

    dados_finais_rp1 = dados_finais_rp1.rename(
        columns=configuracoes["renomear_colunas"]["rp1"]
    )

    timestamp_backup = gerar_timestamp_backup()

    backup_p1 = criar_backup_arquivo(
        caminho_origem=caminho_destino_p1,
        pasta_backups=caminho_backups,
        timestamp=timestamp_backup
    )

    backup_rp1 = criar_backup_arquivo(
        caminho_origem=caminho_destino_rp1,
        pasta_backups=caminho_backups,
        timestamp=timestamp_backup
    )

    if backup_p1 is not None:
        logger.info("Backup P1 criado: %s", backup_p1.name)

    if backup_rp1 is not None:
        logger.info("Backup RP1 criado: %s", backup_rp1.name)

    salvar_excel(
        dados=dados_finais_p1,
        caminho_destino=caminho_destino_p1,
        nome_aba=configuracao_destino_p1["aba"]
    )

    salvar_excel(
        dados=dados_finais_rp1,
        caminho_destino=caminho_destino_rp1,
        nome_aba=configuracao_destino_rp1["aba"]
    )

    logger.info("Processamento incremental concluido.")
    logger.info("Execucao do pipeline finalizada.")
