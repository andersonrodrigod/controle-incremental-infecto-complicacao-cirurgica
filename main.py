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
        executar_pipeline(nomes_fluxos=("p1", "rp1", "p1_sciras"))
    except Exception as erro:
        logger.exception("Execucao falhou: %s", erro)

        try:
            for nome_fluxo in ("p1", "rp1", "p1_sciras"):
                registrar_auditoria_execucao(
                    {
                        "fluxo": nome_fluxo,
                        "status": "FALHA",
                        "mensagem_erro": str(erro)
                    },
                    nome_fluxo=nome_fluxo
                )
        except Exception:
            logger.exception("Nao foi possivel registrar auditoria de falha.")

        exit(1)

    logger.info("Execucao finalizada.")


if __name__ == "__main__":
    main()
