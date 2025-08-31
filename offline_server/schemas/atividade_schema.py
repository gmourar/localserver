from pydantic import BaseModel

class AtividadeRequest(BaseModel):
    method: str
    id_number: str
    is_foreign: bool
    stand_name: str
    tablet_name: str
    client_validated_at: str
