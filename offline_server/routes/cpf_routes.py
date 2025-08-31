from fastapi import APIRouter
from offline_server.schemas.cpf_schema import CPFRequest
from offline_server.controllers.cpf_controller import verificar_cpf_controller

router = APIRouter(prefix="/cpf/status", tags=["CPF"])

@router.post("")
async def verificar(cpf_request: CPFRequest):
    return verificar_cpf_controller(cpf_request)
