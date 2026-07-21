import logging
from datetime import date
from collections.abc import Iterable
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


def executar_pipeline(
    nomes_fluxos: Iterable[str] | None = None
) -> dict[str, Any]:
    logger.info("Iniciando execucao do pipeline...")

    configuracoes = carregar_configuracoes()
    nomes_fluxos_normalizados = _normalizar_fluxos_selecionados(
        nomes_fluxos=nomes_fluxos,
        fluxos_configurados=configuracoes["fluxos"].keys(),
    )
    data_envio = date.today().strftime("%d/%m/%Y")
    timestamp_backup = gerar_timestamp_backup()

    resumo_execucao = _criar_resumo_execucao_base()

    for nome_fluxo in nomes_fluxos_normalizados:
        resumo_fluxo = _executar_fluxo(
            nome_fluxo=nome_fluxo,
            configuracoes=configuracoes,
            data_envio=data_envio,
            timestamp_backup=timestamp_backup,
        )
        _atualizar_resumo_execucao(
            resumo_execucao=resumo_execucao,
            resumo_fluxo=resumo_fluxo,
        )

        try:
            registrar_auditoria_execucao(
                _criar_resumo_auditoria_fluxo(
                    resumo_execucao=resumo_execucao,
                    resumo_fluxo=resumo_fluxo,
                ),
                nome_fluxo=nome_fluxo,
            )
        except Exception:
            logger.exception(
                "Nao foi possivel registrar auditoria de sucesso."
            )

    logger.info("Processamento incremental concluido.")
    logger.info("Execucao do pipeline finalizada.")

    return resumo_execucao


def _normalizar_fluxos_selecionados(
    nomes_fluxos: Iterable[str] | None,
    fluxos_configurados: Iterable[str],
) -> tuple[str, ...]:
    fluxos_disponiveis = tuple(fluxos_configurados)
    fluxos_selecionados = tuple(nomes_fluxos or fluxos_disponiveis)

    for nome_fluxo in fluxos_selecionados:
        if nome_fluxo not in fluxos_disponiveis:
            raise KeyError(f"Fluxo nao configurado: {nome_fluxo}")

    return fluxos_selecionados


def _executar_fluxo(
    nome_fluxo: str,
    configuracoes: dict[str, Any],
    data_envio: str,
    timestamp_backup: str,
) -> dict[str, Any]:
    fluxo = configuracoes["fluxos"][nome_fluxo]
    configuracao_entrada = fluxo["entrada"]
    configuracao_destino = fluxo["destino"]
    schema_colunas = configuracoes.get("schema_colunas")

    caminho_entrada = obter_caminho_fluxo(nome_fluxo, "entrada")
    caminho_destino = obter_caminho_fluxo(nome_fluxo, "destino")
    caminho_backups = obter_caminho_pasta_fluxo(nome_fluxo, "backups")

    dados_entrada = ler_excel(
        caminho_arquivo=caminho_entrada,
        nome_aba=configuracao_entrada["aba"],
    )
    dados_entrada = aplicar_schema_colunas(
        dados=dados_entrada,
        schema_colunas=schema_colunas,
    )

    validar_dataframe_vazio(dados_entrada)
    validar_colunas_obrigatorias(
        dados=dados_entrada,
        colunas_obrigatorias=configuracoes["colunas_obrigatorias"],
    )

    dados_fluxo = _filtrar_registros_fluxo(
        nome_fluxo=nome_fluxo,
        dados_entrada=dados_entrada,
        configuracoes=configuracoes,
    )

    historico = _carregar_historico_fluxo(
        nome_fluxo=nome_fluxo,
        caminho_destino=caminho_destino,
        nome_aba=configuracao_destino["aba"],
        configuracoes=configuracoes,
    )

    novos = identificar_registros_novos(
        dados_atuais=dados_fluxo,
        dados_historico=historico,
        coluna_chave="SENHA",
    )

    rotulo_fluxo = nome_fluxo.upper()

    logger.info("Arquivo %s lido: %s", rotulo_fluxo, caminho_entrada.name)
    logger.info("Aba %s lida: %s", rotulo_fluxo, configuracao_entrada["aba"])
    logger.info("Linhas %s lidas: %s", rotulo_fluxo, dados_entrada.shape[0])
    logger.info("Colunas %s lidas: %s", rotulo_fluxo, dados_entrada.shape[1])
    logger.info(
        "Registros selecionados para %s: %s",
        rotulo_fluxo,
        dados_fluxo.shape[0],
    )
    logger.info("Novos registros para %s: %s", rotulo_fluxo, novos.shape[0])

    dados_finais = mesclar_com_historico_preservando_colunas_manuais(
        dados_atuais=dados_fluxo,
        dados_historico=historico,
        coluna_chave="SENHA",
        colunas_manuais=configuracoes.get("colunas_manuais", {}).get(
            nome_fluxo,
            [],
        ),
        coluna_data_envio="DATA DE ENVIO",
        data_envio=data_envio,
    )
    dados_finais = dados_finais.rename(
        columns=configuracoes["renomear_colunas"][nome_fluxo]
    )

    destino_existente = caminho_destino.exists()

    backup = criar_backup_arquivo(
        caminho_origem=caminho_destino,
        pasta_backups=caminho_backups,
        timestamp=timestamp_backup,
    )

    if backup is not None:
        logger.info("Backup %s criado: %s", rotulo_fluxo, backup.name)

    salvar_excel(
        dados=dados_finais,
        caminho_destino=caminho_destino,
        nome_aba=configuracao_destino["aba"],
        dados_incrementais=(
            dados_finais.tail(novos.shape[0])
            if destino_existente
            else None
        ),
    )

    return {
        "fluxo": nome_fluxo,
        "arquivo_entrada": caminho_entrada.name,
        "aba_entrada": configuracao_entrada["aba"],
        "linhas_lidas": dados_entrada.shape[0],
        "colunas_lidas": dados_entrada.shape[1],
        "registros": dados_fluxo.shape[0],
        "novos": novos.shape[0],
        "linhas_finais": dados_finais.shape[0],
        "backup": backup.name if backup is not None else "",
    }


def _filtrar_registros_fluxo(
    nome_fluxo: str,
    dados_entrada: pd.DataFrame,
    configuracoes: dict[str, Any],
) -> pd.DataFrame:
    regras_processamento = configuracoes["regras_processamento"]

    if nome_fluxo == "p1":
        regra_p1 = regras_processamento["p1"]
        dados_fluxo = filtrar_registros_p1(
            dados=dados_entrada,
            criterios=regra_p1["criterios"],
        )
        return selecionar_colunas_destino(
            dados=dados_fluxo,
            colunas_destino=configuracoes["colunas_destino"]["p1"],
        )

    if nome_fluxo == "rp1":
        regra_rp1 = regras_processamento["rp1"]
        dados_fluxo = filtrar_registros_rp1(
            dados=dados_entrada,
            coluna=regra_rp1["coluna"],
            valor_minimo=regra_rp1["valor_minimo"],
            valor_maximo=regra_rp1["valor_maximo"],
            criterios=regra_rp1["criterios"],
        )
        dados_fluxo = selecionar_colunas_destino(
            dados=dados_fluxo,
            colunas_destino=configuracoes["colunas_destino"]["rp1"],
        )
        return mapear_valores_colunas(
            dados=dados_fluxo,
            mapas_valores=configuracoes.get("mapear_valores", {}).get(
                "rp1",
                {},
            ),
        )

    raise KeyError(f"Fluxo sem regra de processamento: {nome_fluxo}")


def _carregar_historico_fluxo(
    nome_fluxo: str,
    caminho_destino: Any,
    nome_aba: str,
    configuracoes: dict[str, Any],
) -> pd.DataFrame:
    if not caminho_destino.exists():
        return pd.DataFrame()

    historico = ler_excel(
        caminho_arquivo=caminho_destino,
        nome_aba=nome_aba,
    )
    historico = restaurar_nomes_tecnicos(
        dados=historico,
        mapa_renomeacao=configuracoes["renomear_colunas"][nome_fluxo],
    )
    historico = _normalizar_coluna_data_envio_historico(historico)

    return aplicar_schema_colunas(
        dados=historico,
        schema_colunas=configuracoes.get("schema_colunas"),
    )


def _normalizar_coluna_data_envio_historico(
    historico: pd.DataFrame,
) -> pd.DataFrame:
    if "DATA ENVIO" not in historico.columns:
        return historico

    resultado = historico.copy()

    if "DATA DE ENVIO" not in resultado.columns:
        resultado["DATA DE ENVIO"] = pd.NA

    data_envio_legado = resultado["DATA ENVIO"].astype("string").str.strip()
    data_de_envio = resultado["DATA DE ENVIO"].astype("string").str.strip()
    linhas_para_recuperar = data_de_envio.isna() | data_de_envio.eq("")

    resultado.loc[
        linhas_para_recuperar,
        "DATA DE ENVIO",
    ] = data_envio_legado.loc[linhas_para_recuperar]

    return resultado.drop(columns=["DATA ENVIO"])


def _criar_resumo_execucao_base() -> dict[str, Any]:
    return {
        "status": "SUCESSO",
        "arquivo_entrada": "",
        "aba_entrada": "",
        "linhas_lidas": 0,
        "colunas_lidas": 0,
        "arquivo_entrada_p1": "",
        "aba_entrada_p1": "",
        "linhas_lidas_p1": 0,
        "colunas_lidas_p1": 0,
        "arquivo_entrada_rp1": "",
        "aba_entrada_rp1": "",
        "linhas_lidas_rp1": 0,
        "colunas_lidas_rp1": 0,
        "registros_p1": 0,
        "novos_p1": 0,
        "registros_rp1": 0,
        "novos_rp1": 0,
        "linhas_finais_p1": 0,
        "linhas_finais_rp1": 0,
        "backup_p1": "",
        "backup_rp1": "",
        "mensagem_erro": "",
    }


def _atualizar_resumo_execucao(
    resumo_execucao: dict[str, Any],
    resumo_fluxo: dict[str, Any],
) -> None:
    nome_fluxo = resumo_fluxo["fluxo"]

    resumo_execucao.update(
        {
            "arquivo_entrada": resumo_fluxo["arquivo_entrada"],
            "aba_entrada": resumo_fluxo["aba_entrada"],
            "linhas_lidas": resumo_fluxo["linhas_lidas"],
            "colunas_lidas": resumo_fluxo["colunas_lidas"],
            f"arquivo_entrada_{nome_fluxo}": resumo_fluxo[
                "arquivo_entrada"
            ],
            f"aba_entrada_{nome_fluxo}": resumo_fluxo["aba_entrada"],
            f"linhas_lidas_{nome_fluxo}": resumo_fluxo["linhas_lidas"],
            f"colunas_lidas_{nome_fluxo}": resumo_fluxo["colunas_lidas"],
            f"registros_{nome_fluxo}": resumo_fluxo["registros"],
            f"novos_{nome_fluxo}": resumo_fluxo["novos"],
            f"linhas_finais_{nome_fluxo}": resumo_fluxo["linhas_finais"],
            f"backup_{nome_fluxo}": resumo_fluxo["backup"],
        }
    )


def _criar_resumo_auditoria_fluxo(
    resumo_execucao: dict[str, Any],
    resumo_fluxo: dict[str, Any],
) -> dict[str, Any]:
    nome_fluxo = resumo_fluxo["fluxo"]
    outro_fluxo = "rp1" if nome_fluxo == "p1" else "p1"

    return {
        **resumo_execucao,
        "fluxo": nome_fluxo,
        "arquivo_entrada": resumo_fluxo["arquivo_entrada"],
        "aba_entrada": resumo_fluxo["aba_entrada"],
        "linhas_lidas": resumo_fluxo["linhas_lidas"],
        "colunas_lidas": resumo_fluxo["colunas_lidas"],
        f"registros_{outro_fluxo}": 0,
        f"novos_{outro_fluxo}": 0,
        f"linhas_finais_{outro_fluxo}": 0,
        f"backup_{outro_fluxo}": "",
    }
