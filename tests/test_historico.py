import pandas as pd

from services.historico import (
    identificar_registros_novos,
    mesclar_com_historico_preservando_colunas_manuais,
)


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
