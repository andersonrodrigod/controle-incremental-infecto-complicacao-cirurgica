from cli.executor import executar_fluxo_cli


def main() -> None:
    executar_fluxo_cli(
        nome_fluxo="rp1",
        descricao="60 dias",
    )


if __name__ == "__main__":
    main()
