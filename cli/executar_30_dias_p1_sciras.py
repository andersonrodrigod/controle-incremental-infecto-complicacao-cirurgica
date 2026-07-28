from cli.executor import executar_fluxo_cli


def main() -> None:
    executar_fluxo_cli(
        nome_fluxo="p1_sciras",
        descricao="30 dias SCIRAS",
    )


if __name__ == "__main__":
    main()
