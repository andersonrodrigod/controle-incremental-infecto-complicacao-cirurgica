import pandas as pd

from services.processamento import (
    filtrar_registros_p1,
    filtrar_registros_rp1,
    restaurar_nomes_tecnicos,
    selecionar_colunas_destino,
)


def test_filtrar_registros_p1_mantem_apenas_valores_aceitos():
    dados = pd.DataFrame(
        {
            "SENHA": ["100", "101", "102", "103", "104"],
            "P1": ["Sim", " nao ", "Talvez", None, "SIM"],
        }
    )

    resultado = filtrar_registros_p1(
        dados=dados,
        coluna="P1",
        valores_aceitos=["Sim", "Nao"],
    )

    assert resultado["SENHA"].tolist() == ["100", "101", "104"]


def test_filtrar_registros_rp1_mantem_apenas_intervalo_configurado():
    dados = pd.DataFrame(
        {
            "SENHA": ["100", "101", "102", "103", "104", "105"],
            "RP1 Nº": [1, "3", 5, 0, 6, "texto"],
        }
    )

    resultado = filtrar_registros_rp1(
        dados=dados,
        coluna="RP1 Nº",
        valor_minimo=1,
        valor_maximo=5,
    )

    assert resultado["SENHA"].tolist() == ["100", "101", "102"]


def test_selecionar_colunas_destino_preserva_ordem_configurada():
    dados = pd.DataFrame(
        {
            "SENHA": ["100"],
            "USUARIO": ["Maria"],
            "P1": ["Sim"],
        }
    )

    resultado = selecionar_colunas_destino(
        dados=dados,
        colunas_destino=["USUARIO", "SENHA"],
    )

    assert resultado.columns.tolist() == ["USUARIO", "SENHA"]
    assert resultado.iloc[0].to_dict() == {
        "USUARIO": "Maria",
        "SENHA": "100",
    }


def test_restaurar_nomes_tecnicos_reverte_colunas_renomeadas():
    dados = pd.DataFrame(
        {
            "Pergunta final": ["Sim"],
            "SENHA": ["100"],
        }
    )

    resultado = restaurar_nomes_tecnicos(
        dados=dados,
        mapa_renomeacao={"P1": "Pergunta final"},
    )

    assert resultado.columns.tolist() == ["P1", "SENHA"]
