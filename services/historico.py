import pandas as pd


def identificar_registros_novos(
    dados_atuais: pd.DataFrame,
    dados_historico: pd.DataFrame,
    coluna_chave: str
) -> pd.DataFrame:
    """
    Retorna somente os registros que ainda não existem
    no histórico, com base em uma coluna-chave.

    Args:
        dados_atuais:
            DataFrame com os registros filtrados da execução atual.

        dados_historico:
            DataFrame com os registros já gravados no destino.

        coluna_chave:
            Nome da coluna usada para identificar cada registro.

    Returns:
        DataFrame contendo somente os registros novos.
    """

    if dados_historico.empty:
        return dados_atuais.copy()

    chaves_existentes = set(
        dados_historico[coluna_chave]
        .dropna()
        .astype(str)
        .str.strip()
    )

    chaves_atuais = (
        dados_atuais[coluna_chave]
        .astype(str)
        .str.strip()
    )

    registros_novos = dados_atuais.loc[
        ~chaves_atuais.isin(chaves_existentes)
    ].copy()

    return registros_novos