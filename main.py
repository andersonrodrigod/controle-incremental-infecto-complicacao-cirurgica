import logging

from core.logging_config import configurar_logging
from services.pipeline import executar_pipeline


def main() -> None:
    configurar_logging()
    logger = logging.getLogger(__name__)

    logger.info("Iniciando controle incremental...")
    executar_pipeline()
    logger.info("Execucao finalizada.")


if __name__ == "__main__":
    main()
