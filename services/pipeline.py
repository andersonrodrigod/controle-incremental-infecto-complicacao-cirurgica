import logging
from typing import Any

import pandas as pd

from core.caminhos import (
    obter_caminho_fluxo,
    obter_caminho_pasta_fluxo,
)
from core.config import carregar_configuracoes
from services.auditoria import registrar_auditoria_execucao
from services.backup import criar_backup_arquivo, gerar_timestamp_backup
from services.escrita import salvar_excel
from services.historico import (
    identificar_registros_novos,
    mesclar_com_historico_preservando_colunas_manuais,
)
from services.leitura import ler_excel
from services.processamento import (
    filtrar_registros_p1,
    filtrar_registros_rp1,
    mapear_valores_colunas,
    restaurar_nomes_tecnicos,
    selecionar_colunas_destino,
)
from services.tipagem import aplicar_schema_colunas
from services.validacao import (
    validar_colunas_obrigatorias,
    validar_dataframe_vazio,
)


logger = logging.getLogger(__name__)


def executar_pipeline() -> dict[str, Any]:
    logger.info("Iniciando execucao do pipeline...")

    configuracoes = carregar_configuracoes()
    fluxos = configuracoes["fluxos"]
    fluxo_p1 = fluxos["p1"]
    fluxo_rp1 = fluxos["rp1"]

    configuracao_entrada_p1 = fluxo_p1["entrada"]
    configuracao_entrada_rp1 = fluxo_rp1["entrada"]
    configuracao_destino_p1 = fluxo_p1["destino"]
    configuracao_destino_rp1 = fluxo_rp1["destino"]

    regras_processamento = configuracoes["regras_processamento"]
    schema_colunas = configuracoes.get("schema_colunas")

    caminho_entrada_p1 = obter_caminho_fluxo("p1", "entrada")
    caminho_entrada_rp1 = obter_caminho_fluxo("rp1", "entrada")
    caminho_destino_p1 = obter_caminho_fluxo("p1", "destino")
    caminho_destino_rp1 = obter_caminho_fluxo("rp1", "destino")
    caminho_backups_p1 = obter_caminho_pasta_fluxo("p1", "backups")
    caminho_backups_rp1 = obter_caminho_pasta_fluxo("rp1", "backups")

    dados_p1_entrada = ler_excel(
        caminho_arquivo=caminho_entrada_p1,
        nome_aba=configuracao_entrada_p1["aba"],
    )
    dados_p1_entrada = aplicar_schema_colunas(
        dados=dados_p1_entrada,
        schema_colunas=schema_colunas,
    )
    dados_rp1_entrada = ler_excel(
        caminho_arquivo=caminho_entrada_rp1,
        nome_aba=configuracao_entrada_rp1["aba"],
    )
    dados_rp1_entrada = aplicar_schema_colunas(
        dados=dados_rp1_entrada,
        schema_colunas=schema_colunas,
    )

    validar_dataframe_vazio(dados_p1_entrada)
    validar_dataframe_vazio(dados_rp1_entrada)

    validar_colunas_obrigatorias(
        dados=dados_p1_entrada,
        colunas_obrigatorias=configuracoes["colunas_obrigatorias"],
    )
    validar_colunas_obrigatorias(
        dados=dados_rp1_entrada,
        colunas_obrigatorias=configuracoes["colunas_obrigatorias"],
    )

    regra_p1 = regras_processamento["p1"]
    regra_rp1 = regras_processamento["rp1"]

    dados_p1 = filtrar_registros_p1(
        dados=dados_p1_entrada,
        criterios=regra_p1["criterios"],
    )
    dados_p1 = selecionar_colunas_destino(
        dados=dados_p1,
        colunas_destino=configuracoes["colunas_destino"]["p1"],
    )

    dados_rp1 = filtrar_registros_rp1(
        dados=dados_rp1_entrada,
        coluna=regra_rp1["coluna"],
        valor_minimo=regra_rp1["valor_minimo"],
        valor_maximo=regra_rp1["valor_maximo"],
        criterios=regra_rp1["criterios"],
    )
    dados_rp1 = selecionar_colunas_destino(
        dados=dados_rp1,
        colunas_destino=configuracoes["colunas_destino"]["rp1"],
    )
    dados_rp1 = mapear_valores_colunas(
        dados=dados_rp1,
        mapas_valores=configuracoes.get("mapear_valores", {}).get(
            "rp1",
            {},
        ),
    )

    if caminho_destino_p1.exists():
        historico_p1 = ler_excel(
            caminho_arquivo=caminho_destino_p1,
            nome_aba=configuracao_destino_p1["aba"],
        )
        historico_p1 = restaurar_nomes_tecnicos(
            dados=historico_p1,
            mapa_renomeacao=configuracoes["renomear_colunas"]["p1"],
        )
        historico_p1 = aplicar_schema_colunas(
            dados=historico_p1,
            schema_colunas=schema_colunas,
        )
    else:
        historico_p1 = pd.DataFrame()

    if caminho_destino_rp1.exists():
        historico_rp1 = ler_excel(
            caminho_arquivo=caminho_destino_rp1,
            nome_aba=configuracao_destino_rp1["aba"],
        )
        historico_rp1 = restaurar_nomes_tecnicos(
            dados=historico_rp1,
            mapa_renomeacao=configuracoes["renomear_colunas"]["rp1"],
        )
        historico_rp1 = aplicar_schema_colunas(
            dados=historico_rp1,
            schema_colunas=schema_colunas,
        )
    else:
        historico_rp1 = pd.DataFrame()

    novos_p1 = identificar_registros_novos(
        dados_atuais=dados_p1,
        dados_historico=historico_p1,
        coluna_chave="SENHA",
    )
    novos_rp1 = identificar_registros_novos(
        dados_atuais=dados_rp1,
        dados_historico=historico_rp1,
        coluna_chave="SENHA",
    )

    logger.info("Arquivo P1 lido: %s", caminho_entrada_p1.name)
    logger.info("Aba P1 lida: %s", configuracao_entrada_p1["aba"])
    logger.info("Linhas P1 lidas: %s", dados_p1_entrada.shape[0])
    logger.info("Colunas P1 lidas: %s", dados_p1_entrada.shape[1])
    logger.info("Arquivo RP1 lido: %s", caminho_entrada_rp1.name)
    logger.info("Aba RP1 lida: %s", configuracao_entrada_rp1["aba"])
    logger.info("Linhas RP1 lidas: %s", dados_rp1_entrada.shape[0])
    logger.info("Colunas RP1 lidas: %s", dados_rp1_entrada.shape[1])
    logger.info("Registros selecionados para P1: %s", dados_p1.shape[0])
    logger.info("Novos registros para P1: %s", novos_p1.shape[0])
    logger.info("Registros selecionados para RP1: %s", dados_rp1.shape[0])
    logger.info("Novos registros para RP1: %s", novos_rp1.shape[0])

    dados_finais_p1 = mesclar_com_historico_preservando_colunas_manuais(
        dados_atuais=dados_p1,
        dados_historico=historico_p1,
        coluna_chave="SENHA",
        colunas_manuais=configuracoes.get("colunas_manuais", {}).get(
            "p1",
            [],
        ),
    )
    dados_finais_rp1 = mesclar_com_historico_preservando_colunas_manuais(
        dados_atuais=dados_rp1,
        dados_historico=historico_rp1,
        coluna_chave="SENHA",
        colunas_manuais=configuracoes.get("colunas_manuais", {}).get(
            "rp1",
            [],
        ),
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
        pasta_backups=caminho_backups_p1,
        timestamp=timestamp_backup,
    )
    backup_rp1 = criar_backup_arquivo(
        caminho_origem=caminho_destino_rp1,
        pasta_backups=caminho_backups_rp1,
        timestamp=timestamp_backup,
    )

    if backup_p1 is not None:
        logger.info("Backup P1 criado: %s", backup_p1.name)

    if backup_rp1 is not None:
        logger.info("Backup RP1 criado: %s", backup_rp1.name)

    salvar_excel(
        dados=dados_finais_p1,
        caminho_destino=caminho_destino_p1,
        nome_aba=configuracao_destino_p1["aba"],
    )
    salvar_excel(
        dados=dados_finais_rp1,
        caminho_destino=caminho_destino_rp1,
        nome_aba=configuracao_destino_rp1["aba"],
    )

    logger.info("Processamento incremental concluido.")
    logger.info("Execucao do pipeline finalizada.")

    resumo_execucao = {
        "status": "SUCESSO",
        "arquivo_entrada": caminho_entrada_p1.name,
        "aba_entrada": configuracao_entrada_p1["aba"],
        "linhas_lidas": dados_p1_entrada.shape[0],
        "colunas_lidas": dados_p1_entrada.shape[1],
        "arquivo_entrada_p1": caminho_entrada_p1.name,
        "aba_entrada_p1": configuracao_entrada_p1["aba"],
        "linhas_lidas_p1": dados_p1_entrada.shape[0],
        "colunas_lidas_p1": dados_p1_entrada.shape[1],
        "arquivo_entrada_rp1": caminho_entrada_rp1.name,
        "aba_entrada_rp1": configuracao_entrada_rp1["aba"],
        "linhas_lidas_rp1": dados_rp1_entrada.shape[0],
        "colunas_lidas_rp1": dados_rp1_entrada.shape[1],
        "registros_p1": dados_p1.shape[0],
        "novos_p1": novos_p1.shape[0],
        "registros_rp1": dados_rp1.shape[0],
        "novos_rp1": novos_rp1.shape[0],
        "linhas_finais_p1": dados_finais_p1.shape[0],
        "linhas_finais_rp1": dados_finais_rp1.shape[0],
        "backup_p1": backup_p1.name if backup_p1 is not None else "",
        "backup_rp1": backup_rp1.name if backup_rp1 is not None else "",
        "mensagem_erro": "",
    }

    resumo_auditoria_p1 = {
        **resumo_execucao,
        "fluxo": "p1",
        "arquivo_entrada": caminho_entrada_p1.name,
        "aba_entrada": configuracao_entrada_p1["aba"],
        "linhas_lidas": dados_p1_entrada.shape[0],
        "colunas_lidas": dados_p1_entrada.shape[1],
        "registros_rp1": 0,
        "novos_rp1": 0,
        "linhas_finais_rp1": 0,
        "backup_rp1": "",
    }
    resumo_auditoria_rp1 = {
        **resumo_execucao,
        "fluxo": "rp1",
        "arquivo_entrada": caminho_entrada_rp1.name,
        "aba_entrada": configuracao_entrada_rp1["aba"],
        "linhas_lidas": dados_rp1_entrada.shape[0],
        "colunas_lidas": dados_rp1_entrada.shape[1],
        "registros_p1": 0,
        "novos_p1": 0,
        "linhas_finais_p1": 0,
        "backup_p1": "",
    }

    try:
        registrar_auditoria_execucao(resumo_auditoria_p1, nome_fluxo="p1")
        registrar_auditoria_execucao(resumo_auditoria_rp1, nome_fluxo="rp1")
    except Exception:
        logger.exception("Nao foi possivel registrar auditoria de sucesso.")

    return resumo_execucao
