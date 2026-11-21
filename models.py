from pydantic import BaseModel

class Medikament(BaseModel):
    name: str
    dosis: str
    schema: str


class Laborwert(BaseModel):
    name: str
    wert: str
    einheit: str


class ArztbriefErgebnis(BaseModel):
    diagnosen: list[str]
    medikamente: list[Medikament]
    laborwerte: list[Laborwert]
