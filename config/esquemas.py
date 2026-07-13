"""Esquemas operacionais do processamento incremental."""

COLUNAS_MANUAIS = {'p1': [], 'rp1': []}

COLUNAS_OBRIGATORIAS = [
    'FILIAL',
    'BASE',
    'SIGLA',
    'COD FILIAL',
    'ESTADO',
    'SENHA',
    'COMPLICACAO',
    'OBITO',
    'COD USUARIO',
    'USUARIO',
    'DT ENVIO',
    'DT INTERNACAO',
    'DIARIAS',
    'UTI',
    'OBSERVACAO',
    'DATA DE ENVIO',
    'P1',
    'P2',
    'P3',
    'P4',
    'OBSERVACAO DO CLIENTE',
    'ESPECIALISTA',
    'CONTATO RP1',
    'DATA CONTATO RP1',
    'OBSERVACAO DO CLIENTE RP1',
    'RP1',
    'RP1 Nº',
    'LIGACAO EFETIVADA',
    'TIPO',
    'TP ATENDIMENTO',
    'UF',
    'DISTRITO',
    'TELEFONE 1',
    'TELEFONE 2',
    'TELEFONE 3',
    'TELEFONE 4',
    'TELEFONE 5'
]

COLUNAS_DESTINO = {
    'p1': [
        'FILIAL',
        'BASE',
        'SIGLA',
        'COD FILIAL',
        'ESTADO',
        'SENHA',
        'COMPLICACAO',
        'OBITO',
        'COD USUARIO',
        'USUARIO',
        'DT ENVIO',
        'DT INTERNACAO',
        'DIARIAS',
        'UTI',
        'OBSERVACAO',
        'DATA DE ENVIO',
        'P1',
        'P2',
        'ESPECIALISTA',
        'LIGACAO EFETIVADA',
        'TIPO',
        'TP ATENDIMENTO',
        'UF',
        'DISTRITO',
        'TELEFONE 1',
        'TELEFONE 2',
        'TELEFONE 3',
        'TELEFONE 4',
        'TELEFONE 5'
    ],

    'rp1': [
        'FILIAL',
        'BASE',
        'SIGLA',
        'COD FILIAL',
        'ESTADO',
        'SENHA',
        'COMPLICACAO',
        'OBITO',
        'COD USUARIO',
        'USUARIO',
        'DT ENVIO',
        'DT INTERNACAO',
        'DIARIAS',
        'UTI',
        'OBSERVACAO',
        'DATA DE ENVIO',
        'P1',
        'P2',
        'P3',
        'P4',
        'ESPECIALISTA',
        'CONTATO RP1',
        'DATA CONTATO RP1',
        'OBSERVACAO DO CLIENTE RP1',
        'RP1 Nº',
        'RP1',
        'LIGACAO EFETIVADA',
        'TIPO',
        'TP ATENDIMENTO',
        'UF',
        'DISTRITO',
        'TELEFONE 1',
        'TELEFONE 2',
        'TELEFONE 3',
        'TELEFONE 4',
        'TELEFONE 5'
    ]
}

SCHEMA_COLUNAS = {
    'texto': [
        'FILIAL',
        'SIGLA',
        'ESTADO',
        'SENHA',
        'COMPLICACAO',
        'OBITO',
        'COD USUARIO',
        'USUARIO',
        'TELEFONE OPERACIONAL',
        'IDADE',
        'EMPRESA',
        'PLANO',
        'TEMPO PLANO',
        'TP ATENDIMENTO',
        'TRATAMENTO',
        'PRESTADOR',
        'SOLICITANTE',
        'PROCEDIMENTO',
        'OBSERVACAO',
        'CHAVE',
        'OPERADOR',
        'CONTATO',
        'DT ENVIO MANUAL',
        'DATA DO CONTATO',
        'LIDA',
        'STATUS',
        'DATA DE ENVIO',
        'P1',
        'P2',
        'P3',
        'OBSERVACAO DO CLIENTE',
        'OPERADOR RP1',
        'CONTATO RP1',
        'DATA CONTATO RP1',
        'OBSERVACAO DO CLIENTE RP1',
        'RP1',
        'LIGACAO EFETIVADA',
        'ESPECIALISTA',
        'TIPO',
        'UF',
        'DISTRITO',
        'TELEFONE 1',
        'TELEFONE 2',
        'TELEFONE 3',
        'TELEFONE 4',
        'TELEFONE 5',
        'CD_PESSOA',
        'DUPLICADO',
        'STATUS ENVIADO',
        'STATUS ENVIADO.1'
    ],
    'data': [
        'DT ADESAO', 
        'DT AUTORIZACAO', 
        'DT INTERNACAO', 
        'DT ENVIO'
    ],
    'numero': [
        'BASE',
        'COD FILIAL',
        'IDADE T',
        'COD PLANO',
        'DIAS CARENCIA',
        'COD PROCEDIMENTO',
        'DIARIAS',
        'UTI',
        'RESPOSTA',
        'P4',
        'RP1 Nº',
        'Unnamed: 61',
        'Unnamed: 65'
    ],
    'booleano': [
        'DUPLICIDADE'
    ]
}

REGRAS_PROCESSAMENTO = {
    'p1': {'criterios': {'P1': 'Sim', 'P2': 'Sim'}},
    'rp1': {'coluna': 'RP1 Nº', 'valor_minimo': 1, 'valor_maximo': 5, 'criterios': {'P1': 'Sim', 'TIPO': 'VIDEO ABDOMINAL'}}}

MAPEAR_VALORES = {
    'rp1': {
        'RP1': {
            'origem': 'RP1 Nº',
            'valores': {
                '1': '1. Sumiu e não voltou a aparecer',
                '2': '2. Sumiu, mas depois voltou a aparecer',
                '3': '3. Diminuiu, mas nunca desapareceu completamente',
                '4': '4. Permanece do mesmo tamanho desde que surgiu',
                '5': '5. Aumentou de tamanho ao longo do tempo'
            }
        }
    }
}

RENOMEAR_COLUNAS = {
    'p1': {
        'P1': 'Você percebeu caroço no corte da cirurgia?',
        'P2': 'Apresentou secreção com pus no corte da cirurgia?',
        'P3': 'Você recebeu orientações claras sobre os cuidados após a '
              'cirurgia?',
        'P4': 'Em relação à sua experiência, qual nota você daria em uma '
              'escala de 0 a 10?'
    },
    
    'rp1': {
        'P1': 'Você percebeu caroço no corte da cirurgia?',
        'P2': 'Apresentou secreção com pus no corte da cirurgia?',
        'P3': 'Você recebeu orientações claras sobre os cuidados após a '
               'cirurgia?',
        'P4': 'Em relação à sua experiência, qual nota você daria em uma '
               'escala de 0 a 10?',
        'RP1': '1. Você percebeu caroço no corte da cirurgia? 60 dias'
    }
}

ESQUEMAS = {
    "colunas_manuais": COLUNAS_MANUAIS,
    "colunas_obrigatorias": COLUNAS_OBRIGATORIAS,
    "colunas_destino": COLUNAS_DESTINO,
    "schema_colunas": SCHEMA_COLUNAS,
    "regras_processamento": REGRAS_PROCESSAMENTO,
    "mapear_valores": MAPEAR_VALORES,
    "renomear_colunas": RENOMEAR_COLUNAS,
}
