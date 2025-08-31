from fastapi import APIRouter
from offline_server.schemas.atividade_schema import AtividadeRequest
from offline_server.controllers.activity_controller import registrar_atividade_controller

router = APIRouter(prefix="/activity/validate", tags=["Atividades"])

@router.post("")
async def registrar(atividade_request: AtividadeRequest):
    return registrar_atividade_controller(atividade_request)
