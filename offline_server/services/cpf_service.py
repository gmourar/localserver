import re
import datetime
from datetime import UTC
from config import REGISTRO_JSON, ARQUIVO_JSON
from offline_server.utils.file_utils import carregar_dados, salvar_dados


def verificar_cpf(cpf_request: dict) -> dict:
    registros = carregar_dados(REGISTRO_JSON)
    dados = carregar_dados(ARQUIVO_JSON)

    data_hora_atual = datetime.datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

    if cpf_request.get("is_foreign") == False:
        # ===== Usuário brasileiro: valida CPF =====
        cpf_raw = cpf_request.get("cpf", "")

        cpf_formatado = re.sub(r'\D', '', cpf_raw)

        # valida se o CPF segue o padrão correto
        if len(cpf_formatado) != 11 or cpf_formatado == cpf_formatado[0] * 11:
            if len(cpf_request.get("id_number")) != 11:
                return {"status": "error", "message": "CPF deve conter 11 dígitos"}
            return {"status": "error", "message": cpf_formatado}

        # 1º dígito
        soma = sum(int(cpf_formatado[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto

        # 2º dígito
        soma = sum(int(cpf_formatado[i]) * (11 - i) for i in range(9)) + digito1 * 2
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto

        if int(cpf_formatado[9]) != digito1 or int(cpf_formatado[10]) != digito2:
            return {"status": "error", "message": "CPF inválido2"}

        novo_registro = {
            "cpf": cpf_formatado,
            "atividade": cpf_request.get("stand_name", ""),
            "id_tablet": cpf_request.get("tablet_name", ""),
            "data_hora": data_hora_atual,
            "status": "local"
        }

        # Busca usuário no JSON
        usuario_encontrado = None
        for usuario in dados:
            if usuario.get("cpf") == cpf_formatado:
                usuario_encontrado = usuario
                break

        if usuario_encontrado:
            registros.append(novo_registro)
            salvar_dados(registros, REGISTRO_JSON)
            return {"status": "success", "usuario": usuario_encontrado}

        return {"status": "error", "message": "CPF não encontrado"}

    else:
        # ===== Usuário estrangeiro: usa passaporte =====
        passport = cpf_request.get("id_number", "").strip()
        if not passport:
            return {"status": "error", "message": "Campo passaporte obrigatório"}

        # Busca usuário estrangeiro no JSON
        usuario_encontrado = None
        for usuario in dados:
            if usuario.get("id_number") == passport and usuario.get("id_type") == "passport":
                usuario_encontrado = usuario
                break

        if not usuario_encontrado:
            return {"status": "error", "message": "Usuário não encontrado"}

        novo_registro = {
            "id_number": passport,
            "atividade": cpf_request.get("stand_name", ""),
            "id_tablet": cpf_request.get("tablet_name", ""),
            "data_hora": data_hora_atual,
            "status": "local"
        }

        registros.append(novo_registro)
        salvar_dados(registros, REGISTRO_JSON)
        return {"status": "success", "usuario": usuario_encontrado}
