import json
from pathlib import Path
from typing import Any

from config.esquemas import ESQUEMAS


RAIZ_PROJETO = Path(__file__).resolve().parents[1]

CAMINHO_CONFIGURACOES = (
    RAIZ_PROJETO
    / "config"
    / "configuracoes.json"
)


def carregar_configuracoes() -> dict[str, Any]:
    configuracoes = _carregar_json(CAMINHO_CONFIGURACOES)
    configuracoes.update(ESQUEMAS)

    return configuracoes


def _carregar_json(caminho: Path) -> dict[str, Any]:
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo de configuração não encontrado: {caminho}"
        )

    try:
        with caminho.open(mode="r", encoding="utf-8") as arquivo:
            return json.load(arquivo)

    except json.JSONDecodeError as erro:
        raise ValueError(
            f"JSON inválido em {caminho}: {erro}"
        ) from erro
