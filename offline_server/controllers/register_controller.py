from offline_server.schemas.cadastro_schema import CadastroModel
from offline_server.services.register_service import cadastrar_usuario

def cadastrar_controller(usuario: CadastroModel) -> dict:
    return cadastrar_usuario(usuario.dict())
