from offline_server.schemas.cpf_schema import CPFRequest
from offline_server.services.cpf_service import verificar_cpf

def verificar_cpf_controller(cpf_request: CPFRequest) -> dict:
    return verificar_cpf(cpf_request.dict())
