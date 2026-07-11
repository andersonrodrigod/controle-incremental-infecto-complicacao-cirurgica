import pandas as pd
import pytest

from services.validacao import (
    identificar_colunas_ausentes,
    validar_colunas_obrigatorias,
    validar_dataframe_vazio,
)


def test_validar_dataframe_vazio_rejeita_dataframe_sem_registros():
    with pytest.raises(ValueError, match="nao possui registros|não possui registros"):
        validar_dataframe_vazio(pd.DataFrame())


def test_validar_colunas_obrigatorias_rejeita_colunas_ausentes():
    dados = pd.DataFrame(
        {
            "SENHA": ["100"],
            "P1": ["Sim"],
        }
    )

    with pytest.raises(ValueError) as erro:
        validar_colunas_obrigatorias(
            dados=dados,
            colunas_obrigatorias=["SENHA", "P1", "RP1 Nº"],
        )

    assert "RP1 Nº" in str(erro.value)


def test_identificar_colunas_ausentes_retorna_lista_sem_interromper():
    dados = pd.DataFrame(
        {
            "SENHA": ["100"],
            "P1": ["Sim"],
        }
    )

    resultado = identificar_colunas_ausentes(
        dados=dados,
        colunas_esperadas=["SENHA", "P1", "RP1 Nº"],
    )

    assert resultado == ["RP1 Nº"]
