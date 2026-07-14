import logging
from sys import exit

from core.logging_config import configurar_logging
from services.auditoria import registrar_auditoria_execucao
from services.pipeline import executar_pipeline


def executar_fluxo_cli(nome_fluxo: str, descricao: str) -> None:
    configurar_logging()
    logger = logging.getLogger(__name__)

    logger.info("Iniciando controle incremental: %s...", descricao)

    try:
        executar_pipeline(nomes_fluxos=(nome_fluxo,))
    except Exception as erro:
        logger.exception("Execucao falhou: %s", erro)

        try:
            registrar_auditoria_execucao(
                {
                    "fluxo": nome_fluxo,
                    "status": "FALHA",
                    "mensagem_erro": str(erro),
                },
                nome_fluxo=nome_fluxo,
            )
        except Exception:
            logger.exception("Nao foi possivel registrar auditoria de falha.")

        exit(1)

    logger.info("Execucao finalizada: %s.", descricao)
