from pydantic import BaseModel, Extra

class CadastroModel(BaseModel):
    name: str
    email: str
    phone: str
    date_birthday: str
    source: str
    tablet_name: str
    is_foreign: bool = False
    id_type: str
    id_number: str

    class Config:
        extra = Extra.allow  # permite campos extras (ex: client_created_at)
