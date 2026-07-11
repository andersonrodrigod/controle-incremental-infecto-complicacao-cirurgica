import pandas as pd


def filtrar_registros_p1(
    dados: pd.DataFrame,
    coluna: str,
    valores_aceitos: list[str]
) -> pd.DataFrame:
    """
    Mantém somente os registros em que P1 possui
    um dos valores aceitos.
    """

    valores_normalizados = {
        str(valor).strip().casefold()
        for valor in valores_aceitos
    }

    coluna_normalizada = (
        dados[coluna]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    resultado = dados.loc[
        coluna_normalizada.isin(valores_normalizados)
    ].copy()

    return resultado


def filtrar_registros_rp1(
    dados: pd.DataFrame,
    coluna: str,
    valor_minimo: int,
    valor_maximo: int
) -> pd.DataFrame:
    """
    Mantém somente os registros em que RP1 Nº possui
    um valor numérico entre o mínimo e o máximo.
    """

    valores_numericos = pd.to_numeric(
        dados[coluna],
        errors="coerce"
    )

    resultado = dados.loc[
        valores_numericos.between(
            valor_minimo,
            valor_maximo,
            inclusive="both"
        )
    ].copy()

    return resultado


def selecionar_colunas_destino(
    dados: pd.DataFrame,
    colunas_destino: list[str]
) -> pd.DataFrame:
    """
    Seleciona e organiza as colunas que serão enviadas
    ao arquivo de destino.
    """

    return dados.loc[:, colunas_destino].copy()


def renomear_colunas_destino(
    dados: pd.DataFrame,
    mapa_renomeacao: dict[str, str]
) -> pd.DataFrame:
    """
    Troca os nomes técnicos pelos nomes finais que
    aparecerão no Excel.
    """

    return dados.rename(
        columns=mapa_renomeacao
    )


def restaurar_nomes_tecnicos(
    dados: pd.DataFrame,
    mapa_renomeacao: dict[str, str]
) -> pd.DataFrame:
    mapa_inverso = {
        nome_final: nome_original
        for nome_original, nome_final in mapa_renomeacao.items()
    }

    return dados.rename(
        columns=mapa_inverso
    )