import pandas as pd


def normalizar_chave_registro(serie: pd.Series) -> pd.Series:
    return (
        serie
        .astype(str)
        .str.strip()
    )


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
        normalizar_chave_registro(
            dados_historico[coluna_chave].dropna()
        )
    )

    chaves_atuais = normalizar_chave_registro(
        dados_atuais[coluna_chave]
    )

    registros_novos = dados_atuais.loc[
        ~chaves_atuais.isin(chaves_existentes)
    ].copy()

    return registros_novos


def mesclar_com_historico_preservando_colunas_manuais(
    dados_atuais: pd.DataFrame,
    dados_historico: pd.DataFrame,
    coluna_chave: str,
    colunas_manuais: list[str] | None = None
) -> pd.DataFrame:
    if dados_historico.empty:
        return dados_atuais.copy()

    colunas_manuais_configuradas = colunas_manuais or []
    colunas_extras_historico = [
        coluna
        for coluna in dados_historico.columns
        if coluna not in dados_atuais.columns
    ]
    colunas_preservadas = list(
        dict.fromkeys(
            colunas_manuais_configuradas
            + colunas_extras_historico
        )
    )

    dados_atualizados = dados_atuais.copy()
    historico = dados_historico.copy()

    dados_atualizados["_chave_incremental"] = normalizar_chave_registro(
        dados_atualizados[coluna_chave]
    )
    historico["_chave_incremental"] = normalizar_chave_registro(
        historico[coluna_chave]
    )

    dados_atuais_unicos = dados_atualizados.drop_duplicates(
        subset=["_chave_incremental"],
        keep="last"
    )
    historico_unico = historico.drop_duplicates(
        subset=["_chave_incremental"],
        keep="last"
    )

    colunas_resultado = list(
        dict.fromkeys(
            [
                coluna
                for coluna in dados_atualizados.columns
                if coluna != "_chave_incremental"
            ]
            + [
                coluna
                for coluna in historico.columns
                if coluna != "_chave_incremental"
            ]
        )
    )

    for coluna in colunas_preservadas:
        if coluna not in dados_atualizados.columns:
            dados_atualizados[coluna] = pd.NA

        if coluna not in historico_unico.columns:
            continue

        valores_historicos = historico_unico.set_index(
            "_chave_incremental"
        )[coluna]
        chaves_atuais = dados_atualizados["_chave_incremental"]
        valores_preservados = chaves_atuais.map(valores_historicos)

        dados_atualizados[coluna] = dados_atualizados[coluna].where(
            valores_preservados.isna(),
            valores_preservados
        )

    historico_atualizado = historico.copy()
    valores_atuais_por_chave = dados_atuais_unicos.set_index(
        "_chave_incremental"
    )
    chaves_historico = set(historico["_chave_incremental"])

    for indice, linha_historico in historico.iterrows():
        chave = linha_historico["_chave_incremental"]

        if chave not in valores_atuais_por_chave.index:
            continue

        linha_atual = valores_atuais_por_chave.loc[chave]

        for coluna in colunas_resultado:
            if coluna in colunas_preservadas:
                valor_historico = linha_historico.get(coluna, pd.NA)
                if not pd.isna(valor_historico):
                    historico_atualizado.loc[indice, coluna] = valor_historico
                    continue

            if coluna in linha_atual.index:
                historico_atualizado.loc[indice, coluna] = linha_atual[coluna]

    registros_novos = dados_atualizados.loc[
        ~dados_atualizados["_chave_incremental"].isin(chaves_historico)
    ].copy()

    resultado = pd.concat(
        [historico_atualizado, registros_novos],
        ignore_index=True
    )

    resultado = resultado.drop(
        columns=["_chave_incremental"],
        errors="ignore"
    )

    return resultado.loc[:, colunas_resultado]
