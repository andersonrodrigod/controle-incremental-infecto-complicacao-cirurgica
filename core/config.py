import json
from pathlib import Path
from typing import Any


RAIZ_PROJETO = Path(__file__).resolve().parents[1]

CAMINHO_CONFIGURACOES = (
    RAIZ_PROJETO
    / "config"
    / "configuracoes.json"
)


def carregar_configuracoes() -> dict[str, Any]:
    if not CAMINHO_CONFIGURACOES.exists():
        raise FileNotFoundError(
            f"Arquivo de configuração não encontrado: "
            f"{CAMINHO_CONFIGURACOES}"
        )

    try:
        with CAMINHO_CONFIGURACOES.open(
            mode="r",
            encoding="utf-8"
        ) as arquivo:
            return json.load(arquivo)

    except json.JSONDecodeError as erro:
        raise ValueError(
            f"JSON inválido em {CAMINHO_CONFIGURACOES}: {erro}"
        ) from erro