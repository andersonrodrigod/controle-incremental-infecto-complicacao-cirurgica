import logging
from sys import exit

from core.logging_config import configurar_logging
from services.auditoria import registrar_auditoria_execucao
from services.pipeline import executar_pipeline


def main() -> None:
    configurar_logging()
    logger = logging.getLogger(__name__)

    logger.info("Iniciando controle incremental...")
    try:
        executar_pipeline()
    except Exception as erro:
        logger.exception("Execucao falhou: %s", erro)

        try:
            registrar_auditoria_execucao(
                {
                    "status": "FALHA",
                    "mensagem_erro": str(erro)
                }
            )
        except Exception:
            logger.exception("Nao foi possivel registrar auditoria de falha.")

        exit(1)

    logger.info("Execucao finalizada.")


if __name__ == "__main__":
    main()
