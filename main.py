@app.post("/api/configurar")
def atualizar_configuracao(config: Configuracao):
    banco = carregar_banco()

    print("===================================")
    print("CONFIG RECEBIDA:")
    print(config.dict())
    print("HORARIOS PAUSA RECEBIDOS:")
    print(config.horariosPausaPadrao)
    print("===================================")

    if config.whatsYukio is not None:
        banco["whatsYukio"] = config.whatsYukio

    if config.instagramYukio is not None:
        banco["instagramYukio"] = config.instagramYukio

    if config.telegramYukio is not None:
        banco["telegramYukio"] = config.telegramYukio

    if config.senhaYukio is not None:
        banco["senhaYukio"] = config.senhaYukio

    if config.servicos is not None:
        banco["servicos"] = config.servicos

    if config.diasFechados is not None:
        banco["diasFechados"] = config.diasFechados

    if config.horariosPausaPadrao is not None:
        banco["horariosPausaPadrao"] = config.horariosPausaPadrao

    if config.horariosBloqueadosPorData is not None:
        banco["horariosBloqueadosPorData"] = config.horariosBloqueadosPorData

    if config.agendamentos is not None:
        banco["agendamentos"] = config.agendamentos

    salvar_banco(banco)

    print("BANCO SALVO:")
    print(banco["horariosPausaPadrao"])

    return {
        "sucesso": True,
        "banco": banco
    }
