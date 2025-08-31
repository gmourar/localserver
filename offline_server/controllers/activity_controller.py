from offline_server.schemas.atividade_schema import AtividadeRequest
from offline_server.services.activity_service import registrar_atividade

def registrar_atividade_controller(atividade_request: AtividadeRequest) -> dict:
    return registrar_atividade(atividade_request.dict())
