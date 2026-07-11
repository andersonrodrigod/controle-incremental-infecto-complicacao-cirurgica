from pathlib import Path

import pytest

from services.backup import criar_backup_arquivo


def test_criar_backup_arquivo_copia_arquivo_existente(tmp_path):
    origem = tmp_path / "CONTROLE INFECTOLOGIA.xlsx"
    origem.write_text("conteudo", encoding="utf-8")

    backup = criar_backup_arquivo(
        caminho_origem=origem,
        pasta_backups=tmp_path / "backups",
        timestamp="20260711_083522",
    )

    assert backup == (
        tmp_path
        / "backups"
        / "CONTROLE INFECTOLOGIA_20260711_083522.xlsx"
    )
    assert backup.read_text(encoding="utf-8") == "conteudo"
    assert origem.read_text(encoding="utf-8") == "conteudo"


def test_criar_backup_arquivo_preserva_extensao_original(tmp_path):
    origem = tmp_path / "CONTROLE INFECTOLOGIA_RP1.xlsm"
    origem.write_text("conteudo", encoding="utf-8")

    backup = criar_backup_arquivo(
        caminho_origem=origem,
        pasta_backups=tmp_path / "backups",
        timestamp="20260711_083522",
    )

    assert backup.name == (
        "CONTROLE INFECTOLOGIA_RP1_20260711_083522.xlsm"
    )


def test_criar_backup_arquivo_retorna_none_quando_origem_nao_existe(tmp_path):
    backup = criar_backup_arquivo(
        caminho_origem=tmp_path / "nao_existe.xlsx",
        pasta_backups=tmp_path / "backups",
        timestamp="20260711_083522",
    )

    assert backup is None
    assert not (tmp_path / "backups").exists()


def test_criar_backup_arquivo_rejeita_origem_que_nao_e_arquivo(tmp_path):
    with pytest.raises(ValueError):
        criar_backup_arquivo(
            caminho_origem=tmp_path,
            pasta_backups=tmp_path / "backups",
            timestamp="20260711_083522",
        )
