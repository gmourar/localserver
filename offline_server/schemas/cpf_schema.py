from pydantic import BaseModel, Extra
from typing import Optional

class CPFRequest(BaseModel):
    stand_name: str
    tablet_name: str
    is_foreign: bool = False
    cpf: Optional[str] = None        # campo CPF opcional
    id_number: Optional[str] = None  # campo ID opcional

    class Config:
        extra = Extra.allow  # permite campos extras como client_created_at
