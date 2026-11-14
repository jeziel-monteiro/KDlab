from .models import Evento


def registrar_evento(*, ator_id, acao, alvo_id, campos_alterados=()):
    """Participa da transação do chamador; não abre nem confirma outra transação."""
    return Evento.objects.create(
        ator_id=ator_id,
        acao=acao,
        alvo_id=alvo_id,
        campos_alterados=list(campos_alterados),
    )
