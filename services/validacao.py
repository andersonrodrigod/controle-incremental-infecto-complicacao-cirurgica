import pandas as pd


def validar_dataframe_vazio(dados: pd.DataFrame) -> None:
    """
    Verifica se o DataFrame possui registros.

    Args:
        dados:
            DataFrame que será validado.

    Raises:
        ValueError:
            Caso o DataFrame esteja vazio.
    """

    if dados.empty:
        raise ValueError(
            "O arquivo de entrada não possui registros."
        )


def validar_colunas_obrigatorias(
    dados: pd.DataFrame,
    colunas_obrigatorias: list[str]
) -> None:
    """
    Verifica se todas as colunas obrigatórias existem no DataFrame.

    Args:
        dados:
            DataFrame que será validado.

        colunas_obrigatorias:
            Lista com os nomes das colunas necessárias.

    Raises:
        ValueError:
            Caso uma ou mais colunas obrigatórias não existam.
    """

    colunas_ausentes = [
        coluna
        for coluna in colunas_obrigatorias
        if coluna not in dados.columns
    ]

    if colunas_ausentes:
        raise ValueError(
            "Colunas obrigatórias ausentes: "
            f"{colunas_ausentes}"
        )
    

import pandas as pd


def identificar_colunas_ausentes(
    dados: pd.DataFrame,
    colunas_esperadas: list[str]
) -> list[str]:
    """
    Identifica quais colunas esperadas não existem no DataFrame.

    A função não interrompe a execução. Ela apenas retorna
    uma lista com as colunas ausentes.

    Args:
        dados:
            DataFrame lido do arquivo de entrada.

        colunas_esperadas:
            Colunas que deveriam existir no arquivo.

    Returns:
        Lista com os nomes das colunas ausentes.
    """

    colunas_ausentes = [
        coluna
        for coluna in colunas_esperadas
        if coluna not in dados.columns
    ]

    return colunas_ausentes


