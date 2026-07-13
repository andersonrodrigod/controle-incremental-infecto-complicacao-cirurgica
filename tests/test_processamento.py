import pandas as pd

from services.processamento import (
    filtrar_registros_p1,
    filtrar_registros_rp1,
    mapear_valores_colunas,
    restaurar_nomes_tecnicos,
    selecionar_colunas_destino,
)


def test_filtrar_registros_p1_exige_p1_e_p2_sim():
    dados = pd.DataFrame(
        {
            "SENHA": ["100", "101", "102", "103", "104"],
            "P1": ["Sim", "Sim", "Nao", "Sim", " SIM "],
            "P2": ["Sim", "Nao", "Sim", None, " sim "],
        }
    )

    resultado = filtrar_registros_p1(
        dados=dados,
        criterios={"P1": "Sim", "P2": "Sim"},
    )

    assert resultado["SENHA"].tolist() == ["100", "104"]


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


def test_filtrar_registros_rp1_exige_intervalo_p1_sim_e_tipo_video_abdominal():
    dados = pd.DataFrame(
        {
            "SENHA": ["100", "101", "102", "103", "104"],
            "RP1 Nº": [1, 2, 3, 6, "texto"],
            "P1": ["Sim", "Nao", "Sim", "Sim", "Sim"],
            "TIPO": [
                "VIDEO ABDOMINAL",
                "VIDEO ABDOMINAL",
                "CONSULTA",
                "VIDEO ABDOMINAL",
                "VIDEO ABDOMINAL",
            ],
        }
    )

    resultado = filtrar_registros_rp1(
        dados=dados,
        coluna="RP1 Nº",
        valor_minimo=1,
        valor_maximo=5,
        criterios={"P1": "Sim", "TIPO": "VIDEO ABDOMINAL"},
    )

    assert resultado["SENHA"].tolist() == ["100"]


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


def test_mapear_valores_colunas_cria_rp1_texto_preservando_rp1_numero():
    dados = pd.DataFrame(
        {
            "SENHA": ["100", "101", "102", "103"],
            "RP1 Nº": [1, "2", 3.0, "texto"],
            "RP1": [pd.NA, pd.NA, pd.NA, pd.NA],
        }
    )

    resultado = mapear_valores_colunas(
        dados=dados,
        mapas_valores={
            "RP1": {
                "origem": "RP1 Nº",
                "valores": {
                    "1": "1. Sumiu e não voltou a aparecer",
                    "2": "2. Sumiu, mas depois voltou a aparecer",
                    "3": "3. Diminuiu, mas nunca desapareceu completamente",
                },
            }
        },
    )

    assert resultado["RP1 Nº"].tolist() == [1, "2", 3.0, "texto"]
    assert resultado["RP1"].tolist() == [
        "1. Sumiu e não voltou a aparecer",
        "2. Sumiu, mas depois voltou a aparecer",
        "3. Diminuiu, mas nunca desapareceu completamente",
        "texto",
    ]


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
