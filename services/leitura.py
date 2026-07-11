from pathlib import Path

import pandas as pd


def ler_excel(
    caminho_arquivo: str | Path,
    nome_aba: str | int = 0
) -> pd.DataFrame:
    """
    Lê uma aba de um arquivo Excel e retorna um DataFrame.

    Args:
        caminho_arquivo:
            Caminho completo ou relativo do arquivo Excel.

        nome_aba:
            Nome da aba ou posição da aba.
            O valor 0 representa a primeira aba.

    Returns:
        DataFrame com os dados da aba selecionada.
    """

    caminho = Path(caminho_arquivo)

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    if not caminho.is_file():
        raise ValueError(
            f"O caminho informado não representa um arquivo: {caminho}"
        )

    if caminho.suffix.lower() not in {".xlsx", ".xlsm", ".xls"}:
        raise ValueError(
            f"Formato de arquivo não suportado: {caminho.suffix}"
        )

    try:
        dataframe = pd.read_excel(
            caminho,
            sheet_name=nome_aba
        )

    except ValueError as erro:
        raise ValueError(
            f"Não foi possível localizar ou ler a aba "
            f"'{nome_aba}' no arquivo '{caminho.name}'."
        ) from erro

    except PermissionError as erro:
        raise PermissionError(
            f"Sem permissão para acessar o arquivo: {caminho}"
        ) from erro

    return dataframe


def listar_abas_excel(
    caminho_arquivo: str | Path
) -> list[str]:
    """
    Retorna os nomes das abas existentes em um arquivo Excel.
    """

    caminho = Path(caminho_arquivo)

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )
    
    if not caminho.is_file():
        raise ValueError(
            f"O caminho informado não representa um arquivo: {caminho}"
        )
    
    if caminho.suffix.lower() not in {".xlsx", ".xlsm", ".xls"}:
        raise ValueError(
            f"Formato de arquivo não suportado: {caminho.suffix}"
        )

    try:
        with pd.ExcelFile(caminho) as arquivo_excel:
            return [str(aba) for aba in arquivo_excel.sheet_names]

    except PermissionError as erro:
        raise PermissionError(
            f"Sem permissão para acessar o arquivo: {caminho}"
        ) from erro

    except Exception as erro:
        raise RuntimeError(
            f"Não foi possível inspecionar o arquivo "
            f"'{caminho.name}'."
        ) from erro