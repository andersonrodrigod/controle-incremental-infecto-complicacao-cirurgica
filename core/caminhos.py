from pathlib import Path
from typing import Any

from core.config import carregar_configuracoes


RAIZ_PROJETO = Path(__file__).resolve().parents[1]


def obter_caminho_base() -> Path:
    configuracoes = carregar_configuracoes()
    caminho_configurado = configuracoes.get("caminho_base")

    if not caminho_configurado:
        return RAIZ_PROJETO

    caminho_base = Path(caminho_configurado)

    if caminho_base.is_absolute():
        return caminho_base

    return RAIZ_PROJETO / caminho_base


def obter_caminho_pasta(nome_pasta: str) -> Path:
    configuracoes = carregar_configuracoes()
    pastas = configuracoes["pastas"]

    if nome_pasta not in pastas:
        raise KeyError(
            f"Pasta não configurada: {nome_pasta}"
        )

    return obter_caminho_base() / pastas[nome_pasta]


def obter_caminho_arquivo(
    nome_arquivo_configurado: str
) -> Path:
    configuracoes = carregar_configuracoes()

    arquivos: dict[str, Any] = configuracoes["arquivos"]
    pastas: dict[str, str] = configuracoes["pastas"]

    mapa_pastas = {
        "entrada": "entrada",
        "destino_p1": "destino",
        "destino_rp1": "destino",
        "auditoria": "auditoria"
    }

    if nome_arquivo_configurado not in arquivos:
        raise KeyError(
            f"Arquivo não configurado: "
            f"{nome_arquivo_configurado}"
        )

    if nome_arquivo_configurado not in mapa_pastas:
        raise KeyError(
            f"Não existe pasta associada ao arquivo: "
            f"{nome_arquivo_configurado}"
        )

    chave_pasta = mapa_pastas[nome_arquivo_configurado]

    if chave_pasta not in pastas:
        raise KeyError(
            f"Pasta não configurada: "
            f"{chave_pasta}"
        )

    caminho_relativo_pasta = pastas[chave_pasta]
    nome_arquivo = arquivos[nome_arquivo_configurado]["nome"]

    return (
        obter_caminho_base()
        / caminho_relativo_pasta
        / nome_arquivo
    )


def obter_caminho_log() -> Path:
    configuracoes = carregar_configuracoes()
    pastas = configuracoes["pastas"]
    arquivos = configuracoes["arquivos"]

    if "logs" not in pastas:
        raise KeyError("Pasta nao configurada: logs")

    if "log" not in arquivos:
        raise KeyError("Arquivo nao configurado: log")

    return (
        obter_caminho_base()
        / pastas["logs"]
        / arquivos["log"]["nome"]
    )
