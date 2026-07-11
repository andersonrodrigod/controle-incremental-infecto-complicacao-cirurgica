import logging
from logging import Logger

from core.caminhos import obter_caminho_log
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

    caminho_log = obter_caminho_log()
    caminho_log.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    logging.basicConfig(
        level=nivel,
        format=FORMATO_LOG,
        datefmt=FORMATO_DATA_LOG,
        handlers=[
            logging.FileHandler(
                caminho_log,
                encoding="utf-8"
            ),
            logging.StreamHandler()
        ],
        force=True
    )

    return logging.getLogger(__name__)
