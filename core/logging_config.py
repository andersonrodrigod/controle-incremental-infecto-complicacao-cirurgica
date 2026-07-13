import logging
from logging import Logger

from core.caminhos import obter_caminho_fluxo
from core.config import carregar_configuracoes


FORMATO_LOG = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
FORMATO_DATA_LOG = "%Y-%m-%d %H:%M:%S"


def configurar_logging() -> Logger:
    configuracoes = carregar_configuracoes()
    nivel_configurado = configuracoes.get("logging", {}).get(
        "nivel",
        "INFO"
    )
    nivel = getattr(
        logging,
        str(nivel_configurado).upper(),
        logging.INFO
    )

    caminhos_log = []

    for nome_fluxo in configuracoes.get("fluxos", {}):
        fluxo = configuracoes["fluxos"][nome_fluxo]
        if "log" in fluxo:
            caminhos_log.append(obter_caminho_fluxo(nome_fluxo, "log"))

    handlers = []

    for caminho_log in dict.fromkeys(caminhos_log):
        caminho_log.parent.mkdir(
            parents=True,
            exist_ok=True
        )
        handlers.append(
            logging.FileHandler(
                caminho_log,
                encoding="utf-8"
            )
        )

    handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=nivel,
        format=FORMATO_LOG,
        datefmt=FORMATO_DATA_LOG,
        handlers=handlers,
        force=True
    )

    return logging.getLogger(__name__)
