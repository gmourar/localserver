from fastapi import APIRouter
from fastapi.responses import JSONResponse
from offline_server.schemas.cadastro_schema import CadastroModel
from offline_server.controllers.register_controller import cadastrar_controller
import re

router = APIRouter(prefix="/register", tags=["Cadastro"])

@router.post("")
async def cadastrar(usuario: CadastroModel):
    return cadastrar_controller(usuario)
