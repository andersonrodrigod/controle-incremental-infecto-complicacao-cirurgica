from typing import Any

import pandas as pd


def aplicar_schema_colunas(
    dados: pd.DataFrame,
    schema_colunas: dict[str, list[str]] | None
) -> pd.DataFrame:
    if not schema_colunas:
        return dados.copy()

    resultado = dados.copy()

    for coluna in schema_colunas.get("texto", []):
        if coluna in resultado.columns:
            resultado[coluna] = resultado[coluna].astype("string")

    for coluna in schema_colunas.get("numero", []):
        if coluna in resultado.columns:
            resultado[coluna] = pd.to_numeric(
                resultado[coluna],
                errors="coerce"
            )

    for coluna in schema_colunas.get("data", []):
        if coluna in resultado.columns:
            resultado[coluna] = pd.to_datetime(
                resultado[coluna],
                errors="coerce"
            )

    for coluna in schema_colunas.get("booleano", []):
        if coluna in resultado.columns:
            resultado[coluna] = _converter_booleano(resultado[coluna])

    return resultado


def _converter_booleano(serie: pd.Series) -> pd.Series:
    valores_texto = (
        serie
        .astype("string")
        .str.strip()
        .str.casefold()
    )
    mapa_booleano: dict[str, Any] = {
        "true": True,
        "1": True,
        "sim": True,
        "s": True,
        "yes": True,
        "false": False,
        "0": False,
        "nao": False,
        "não": False,
        "n": False,
        "no": False,
    }

    return valores_texto.map(mapa_booleano).astype("boolean")
