import logging

from core import logging_config


def test_configurar_logging_grava_mensagem_em_arquivo_utf8(
    monkeypatch,
    tmp_path
):
    caminho_log = tmp_path / "execucoes.log"
    monkeypatch.setattr(
        logging_config,
        "obter_caminho_fluxo",
        lambda nome_fluxo, tipo_caminho: caminho_log
    )
    monkeypatch.setattr(
        logging_config,
        "carregar_configuracoes",
        lambda: {
            "logging": {"nivel": "INFO"},
            "fluxos": {
                "p1": {
                    "log": {
                        "nome": "execucoes.log"
                    }
                }
            }
        }
    )

    logging_config.configurar_logging()

    logging.getLogger("teste").info("Execucao com acento: infecção")

    conteudo = caminho_log.read_text(encoding="utf-8")
    assert "Execucao com acento: infecção" in conteudo
