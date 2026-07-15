import pandas as pd

from services.pipeline import _normalizar_coluna_data_envio_historico


def test_normalizar_coluna_data_envio_historico_remove_nome_legado():
    historico = pd.DataFrame(
        {
            "SENHA": ["100", "101"],
            "DATA DE ENVIO": ["13/07/2026", ""],
            "DATA ENVIO": ["valor legado ignorado", "14/07/2026"],
        }
    )

    resultado = _normalizar_coluna_data_envio_historico(historico)

    assert "DATA ENVIO" not in resultado.columns
    assert resultado["DATA DE ENVIO"].tolist() == [
        "13/07/2026",
        "14/07/2026",
    ]
