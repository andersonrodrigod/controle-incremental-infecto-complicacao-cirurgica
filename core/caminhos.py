from pathlib import Path
from typing import Any

from core.config import carregar_configuracoes


RAIZ_PROJETO = Path(__file__).resolve().parents[1]


def resolver_caminho_base(caminho_configurado: str | None) -> Path:
    if not caminho_configurado:
        return RAIZ_PROJETO

    caminho_base = Path(caminho_configurado)

    if caminho_base.is_absolute():
        return caminho_base

    return RAIZ_PROJETO / caminho_base


def obter_caminho_fluxo(
    nome_fluxo: str,
    tipo_caminho: str
) -> Path:
    configuracoes = carregar_configuracoes()
    fluxos: dict[str, Any] = configuracoes["fluxos"]

    if nome_fluxo not in fluxos:
        raise KeyError(f"Fluxo nao configurado: {nome_fluxo}")

    fluxo = fluxos[nome_fluxo]

    if tipo_caminho not in fluxo:
        raise KeyError(
            f"Caminho nao configurado no fluxo {nome_fluxo}: "
            f"{tipo_caminho}"
        )

    configuracao_caminho = fluxo[tipo_caminho]

    return (
        resolver_caminho_base(
            configuracao_caminho.get("caminho_base")
        )
        / configuracao_caminho.get("pasta", "")
        / configuracao_caminho["nome"]
    )


def obter_caminho_pasta_fluxo(
    nome_fluxo: str,
    tipo_caminho: str
) -> Path:
    configuracoes = carregar_configuracoes()
    fluxos: dict[str, Any] = configuracoes["fluxos"]

    if nome_fluxo not in fluxos:
        raise KeyError(f"Fluxo nao configurado: {nome_fluxo}")

    fluxo = fluxos[nome_fluxo]

    if tipo_caminho not in fluxo:
        raise KeyError(
            f"Pasta nao configurada no fluxo {nome_fluxo}: "
            f"{tipo_caminho}"
        )

    configuracao_caminho = fluxo[tipo_caminho]

    return (
        resolver_caminho_base(
            configuracao_caminho.get("caminho_base")
        )
        / configuracao_caminho.get("pasta", "")
    )
