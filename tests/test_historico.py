import warnings

import pandas as pd

from services.historico import (
    identificar_registros_novos,
    mesclar_com_historico_preservando_colunas_manuais,
)
from services.tipagem import aplicar_schema_colunas


def test_identificar_registros_novos_remove_senhas_ja_existentes():
    dados_atuais = pd.DataFrame(
        {
            "SENHA": ["100", "101", "102", "103"],
            "USUARIO": ["A", "B", "C", "D"],
        }
    )
    dados_historico = pd.DataFrame(
        {
            "SENHA": ["100", "101"],
            "USUARIO": ["A", "B"],
        }
    )

    resultado = identificar_registros_novos(
        dados_atuais=dados_atuais,
        dados_historico=dados_historico,
        coluna_chave="SENHA",
    )

    assert resultado["SENHA"].tolist() == ["102", "103"]


def test_identificar_registros_novos_normaliza_espacos_na_senha():
    dados_atuais = pd.DataFrame(
        {
            "SENHA": ["100", "101", " 102 "],
        }
    )
    dados_historico = pd.DataFrame(
        {
            "SENHA": [" 100 ", "102"],
        }
    )

    resultado = identificar_registros_novos(
        dados_atuais=dados_atuais,
        dados_historico=dados_historico,
        coluna_chave="SENHA",
    )

    assert resultado["SENHA"].tolist() == ["101"]


def test_identificar_registros_novos_retorna_todos_quando_historico_vazio():
    dados_atuais = pd.DataFrame(
        {
            "SENHA": ["100", "101"],
        }
    )
    dados_historico = pd.DataFrame()

    resultado = identificar_registros_novos(
        dados_atuais=dados_atuais,
        dados_historico=dados_historico,
        coluna_chave="SENHA",
    )

    assert resultado["SENHA"].tolist() == ["100", "101"]
    assert resultado is not dados_atuais


def test_mesclar_com_historico_preserva_colunas_extras_manuais():
    dados_atuais = pd.DataFrame(
        {
            "SENHA": ["100", "101"],
            "USUARIO": ["Maria atualizada", "Joao"],
        }
    )
    dados_historico = pd.DataFrame(
        {
            "SENHA": ["100"],
            "USUARIO": ["Maria antiga"],
            "CLASSIFICACAO MANUAL": ["Revisado"],
        }
    )

    resultado = mesclar_com_historico_preservando_colunas_manuais(
        dados_atuais=dados_atuais,
        dados_historico=dados_historico,
        coluna_chave="SENHA",
    )

    linha_100 = resultado.loc[resultado["SENHA"] == "100"].iloc[0]
    linha_101 = resultado.loc[resultado["SENHA"] == "101"].iloc[0]

    assert linha_100["USUARIO"] == "Maria atualizada"
    assert linha_100["CLASSIFICACAO MANUAL"] == "Revisado"
    assert pd.isna(linha_101["CLASSIFICACAO MANUAL"])


def test_mesclar_com_historico_preserva_coluna_configurada_sobreposta():
    dados_atuais = pd.DataFrame(
        {
            "SENHA": ["100"],
            "STATUS": ["Novo valor"],
        }
    )
    dados_historico = pd.DataFrame(
        {
            "SENHA": ["100"],
            "STATUS": ["Valor manual"],
        }
    )

    resultado = mesclar_com_historico_preservando_colunas_manuais(
        dados_atuais=dados_atuais,
        dados_historico=dados_historico,
        coluna_chave="SENHA",
        colunas_manuais=["STATUS"],
    )

    assert resultado.loc[0, "STATUS"] == "Valor manual"


def test_mesclar_com_historico_mantem_registros_antigos_fora_da_entrada():
    dados_atuais = pd.DataFrame(
        {
            "SENHA": ["101"],
            "USUARIO": ["Joao"],
        }
    )
    dados_historico = pd.DataFrame(
        {
            "SENHA": ["100"],
            "USUARIO": ["Maria"],
            "CLASSIFICACAO MANUAL": ["Revisado"],
        }
    )

    resultado = mesclar_com_historico_preservando_colunas_manuais(
        dados_atuais=dados_atuais,
        dados_historico=dados_historico,
        coluna_chave="SENHA",
    )

    assert resultado["SENHA"].tolist() == ["100", "101"]


def test_mesclar_com_historico_atualiza_existente_no_lugar_e_append_novo():
    dados_atuais = pd.DataFrame(
        {
            "SENHA": ["100", "101", "102"],
            "USUARIO": ["Maria atualizada", "Joao atualizado", "Ana"],
            "DATA DE ENVIO": ["", "", ""],
        }
    )
    dados_historico = pd.DataFrame(
        {
            "SENHA": ["100", "101"],
            "USUARIO": ["Maria antiga", "Joao antigo"],
            "DATA DE ENVIO": ["", "eu"],
        }
    )

    resultado = mesclar_com_historico_preservando_colunas_manuais(
        dados_atuais=dados_atuais,
        dados_historico=dados_historico,
        coluna_chave="SENHA",
        colunas_manuais=["DATA DE ENVIO"],
    )

    assert resultado["SENHA"].tolist() == ["100", "101", "102"]
    assert resultado["USUARIO"].tolist() == [
        "Maria atualizada",
        "Joao atualizado",
        "Ana",
    ]
    assert resultado.loc[1, "DATA DE ENVIO"] == "eu"


def test_mesclar_com_historico_preenche_data_envio_texto_em_registros_novos():
    dados_atuais = pd.DataFrame(
        {
            "SENHA": ["100", "101"],
            "USUARIO": ["Maria atualizada", "Joao"],
            "DATA DE ENVIO": ["", "valor anterior"],
        }
    )
    dados_historico = pd.DataFrame(
        {
            "SENHA": ["100"],
            "USUARIO": ["Maria antiga"],
            "DATA DE ENVIO": ["13/07/2026"],
        }
    )

    resultado = mesclar_com_historico_preservando_colunas_manuais(
        dados_atuais=dados_atuais,
        dados_historico=dados_historico,
        coluna_chave="SENHA",
        coluna_data_envio="DATA DE ENVIO",
        data_envio="14/07/2026",
    )

    linha_existente = resultado.loc[resultado["SENHA"] == "100"].iloc[0]
    linha_nova = resultado.loc[resultado["SENHA"] == "101"].iloc[0]

    assert linha_existente["DATA DE ENVIO"] == "13/07/2026"
    assert linha_nova["DATA DE ENVIO"] == "14/07/2026"
    assert isinstance(linha_nova["DATA DE ENVIO"], str)


def test_mesclar_com_historico_cria_data_envio_quando_coluna_nao_existe():
    dados_atuais = pd.DataFrame(
        {
            "SENHA": ["101"],
            "USUARIO": ["Joao"],
        }
    )
    dados_historico = pd.DataFrame(
        {
            "SENHA": ["100"],
            "USUARIO": ["Maria"],
        }
    )

    resultado = mesclar_com_historico_preservando_colunas_manuais(
        dados_atuais=dados_atuais,
        dados_historico=dados_historico,
        coluna_chave="SENHA",
        coluna_data_envio="DATA DE ENVIO",
        data_envio="14/07/2026",
    )

    linha_nova = resultado.loc[resultado["SENHA"] == "101"].iloc[0]

    assert "DATA DE ENVIO" in resultado.columns
    assert "DATA ENVIO" not in resultado.columns
    assert linha_nova["DATA DE ENVIO"] == "14/07/2026"


def test_mesclar_com_historico_aceita_mistura_de_numero_e_texto_sem_warning():
    dados_atuais = pd.DataFrame(
        {
            "SENHA": ["100"],
            "TELEFONE 1": ["5585992493600"],
        }
    )
    dados_historico = pd.DataFrame(
        {
            "SENHA": ["100"],
            "TELEFONE 1": [5585992493600],
        }
    )
    schema_colunas = {
        "texto": ["SENHA", "TELEFONE 1"],
    }
    dados_atuais = aplicar_schema_colunas(
        dados=dados_atuais,
        schema_colunas=schema_colunas,
    )
    dados_historico = aplicar_schema_colunas(
        dados=dados_historico,
        schema_colunas=schema_colunas,
    )

    with warnings.catch_warnings():
        warnings.simplefilter("error", FutureWarning)
        resultado = mesclar_com_historico_preservando_colunas_manuais(
            dados_atuais=dados_atuais,
            dados_historico=dados_historico,
            coluna_chave="SENHA",
        )

    assert resultado.loc[0, "TELEFONE 1"] == "5585992493600"


def test_mesclar_com_historico_nao_emite_futurewarning_com_vazio_em_coluna_numerica():
    dados_atuais = pd.DataFrame(
        {
            "SENHA": ["100", "101"],
            "RP1 NÂº": ["", ""],
            "AUDITORIA MEDICA": ["", ""],
            "DATA DE ENVIO": ["", ""],
        }
    )
    dados_historico = pd.DataFrame(
        {
            "SENHA": ["100"],
            "RP1 NÂº": [1.0],
            "AUDITORIA MEDICA": [pd.NA],
            "DATA DE ENVIO": ["13/07/2026"],
        }
    )

    with warnings.catch_warnings():
        warnings.simplefilter("error", FutureWarning)
        resultado = mesclar_com_historico_preservando_colunas_manuais(
            dados_atuais=dados_atuais,
            dados_historico=dados_historico,
            coluna_chave="SENHA",
            colunas_manuais=["AUDITORIA MEDICA"],
            coluna_data_envio="DATA DE ENVIO",
            data_envio="14/07/2026",
        )

    assert resultado["SENHA"].tolist() == ["100", "101"]
    assert resultado.loc[0, "RP1 NÂº"] == ""
    assert resultado.loc[1, "DATA DE ENVIO"] == "14/07/2026"
