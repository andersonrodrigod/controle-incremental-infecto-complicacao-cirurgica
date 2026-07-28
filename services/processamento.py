import unicodedata

import pandas as pd


def _remover_acentos(texto: str) -> str:
    return "".join(
        caractere
        for caractere in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caractere)
    )


def _normalizar_texto(serie: pd.Series) -> pd.Series:
    return (
        serie
        .astype("string")
        .str.strip()
        .str.casefold()
        .map(_remover_acentos, na_action="ignore")
    )


def _criar_mascara_criterios_texto(
    dados: pd.DataFrame,
    criterios: dict[str, str]
) -> pd.Series:
    mascara = pd.Series(True, index=dados.index)

    for coluna, valor_esperado in criterios.items():
        valor_normalizado = _remover_acentos(
            str(valor_esperado).strip().casefold()
        )
        mascara = mascara & (
            _normalizar_texto(dados[coluna]) == valor_normalizado
        )

    return mascara


def _criar_mascara_criterios_opcoes_texto(
    dados: pd.DataFrame,
    criterios_opcoes: dict[str, list[str]]
) -> pd.Series:
    mascara = pd.Series(True, index=dados.index)

    for coluna, valores_esperados in criterios_opcoes.items():
        valores_normalizados = {
            _remover_acentos(str(valor).strip().casefold())
            for valor in valores_esperados
        }
        mascara = mascara & (
            _normalizar_texto(dados[coluna]).isin(valores_normalizados)
        )

    return mascara


def filtrar_registros_p1(
    dados: pd.DataFrame,
    criterios: dict[str, str]
) -> pd.DataFrame:
    """
    Mantem somente os registros que atendem aos
    criterios textuais configurados para o destino P1.
    """

    resultado = dados.loc[
        _criar_mascara_criterios_texto(dados, criterios)
    ].copy()

    return resultado


def filtrar_registros_opcoes_texto(
    dados: pd.DataFrame,
    criterios_opcoes: dict[str, list[str]]
) -> pd.DataFrame:
    """
    Mantem registros em que as colunas configuradas possuem
    um dos valores textuais esperados.
    """

    resultado = dados.loc[
        _criar_mascara_criterios_opcoes_texto(dados, criterios_opcoes)
    ].copy()

    return resultado


def filtrar_registros_rp1(
    dados: pd.DataFrame,
    coluna: str,
    valor_minimo: int,
    valor_maximo: int,
    criterios: dict[str, str] | None = None
) -> pd.DataFrame:
    """
    Mantem somente os registros em que RP1 No possui
    um valor numerico entre o minimo e o maximo e
    atende aos criterios textuais configurados.
    """

    valores_numericos = pd.to_numeric(
        dados[coluna],
        errors="coerce"
    )

    mascara = valores_numericos.between(
        valor_minimo,
        valor_maximo,
        inclusive="both"
    )

    if criterios:
        mascara = mascara & _criar_mascara_criterios_texto(
            dados=dados,
            criterios=criterios
        )

    resultado = dados.loc[mascara].copy()

    return resultado


def selecionar_colunas_destino(
    dados: pd.DataFrame,
    colunas_destino: list[str]
) -> pd.DataFrame:
    """
    Seleciona e organiza as colunas que serao enviadas
    ao arquivo de destino.
    """

    resultado = dados.copy()

    for coluna in colunas_destino:
        if coluna not in resultado.columns:
            resultado[coluna] = ""

    return resultado.loc[:, colunas_destino].copy()


def _normalizar_valor_mapa(valor: object) -> str | None:
    if pd.isna(valor): #type: ignore
        return None

    valor_texto = str(valor).strip()

    try:
        valor_numerico = float(valor_texto)
    except ValueError:
        return valor_texto

    if valor_numerico.is_integer():
        return str(int(valor_numerico))

    return valor_texto


def mapear_valores_colunas(
    dados: pd.DataFrame,
    mapas_valores: dict[str, dict[str, str | dict[str, str]]]
) -> pd.DataFrame:
    """
    Troca valores tecnicos por textos finais configurados,
    preservando valores que nao estejam no mapa.
    """

    resultado = dados.copy()

    for coluna_destino, configuracao_mapa in mapas_valores.items():
        if (
            "origem" in configuracao_mapa
            and "valores" in configuracao_mapa
        ):
            coluna_origem = str(configuracao_mapa["origem"])
            mapa = configuracao_mapa["valores"]
        else:
            coluna_origem = coluna_destino
            mapa = configuracao_mapa

        if coluna_origem not in resultado.columns:
            continue

        resultado[coluna_destino] = resultado[coluna_origem].map(
            lambda valor: mapa.get( #type: ignore
                _normalizar_valor_mapa(valor), #type: ignore
                valor
            ) 
        )

    return resultado


def renomear_colunas_destino(
    dados: pd.DataFrame,
    mapa_renomeacao: dict[str, str]
) -> pd.DataFrame:
    """
    Troca os nomes tecnicos pelos nomes finais que
    aparecerao no Excel.
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
