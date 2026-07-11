from datetime import datetime
from pathlib import Path
from shutil import copy2


FORMATO_TIMESTAMP_BACKUP = "%Y%m%d_%H%M%S"


def gerar_timestamp_backup() -> str:
    return datetime.now().strftime(FORMATO_TIMESTAMP_BACKUP)


def criar_backup_arquivo(
    caminho_origem: str | Path,
    pasta_backups: str | Path,
    timestamp: str | None = None
) -> Path | None:
    caminho = Path(caminho_origem)

    if not caminho.exists():
        return None

    if not caminho.is_file():
        raise ValueError(
            f"O caminho informado nao representa um arquivo: {caminho}"
        )

    pasta_destino = Path(pasta_backups)
    pasta_destino.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp_backup = timestamp or gerar_timestamp_backup()
    nome_backup = (
        f"{caminho.stem}_{timestamp_backup}{caminho.suffix}"
    )
    caminho_backup = pasta_destino / nome_backup

    copy2(caminho, caminho_backup)

    return caminho_backup
