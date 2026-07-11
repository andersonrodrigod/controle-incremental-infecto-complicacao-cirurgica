import pandas as pd

from services.historico import identificar_registros_novos


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
