from pathlib import Path

import pandas as pd


def salvar_excel(
    dados: pd.DataFrame,
    caminho_destino: str | Path,
    nome_aba: str
) -> None:
    """
    Salva um DataFrame em um arquivo Excel.

    Se a pasta não existir, ela será criada.
    Se o arquivo já existir, será substituído.
    """

    caminho = Path(caminho_destino)

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dados.to_excel(
        caminho,
        sheet_name=nome_aba,
        index=False
    )