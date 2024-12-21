from pydantic import BaseModel

class TermSchema(BaseModel):
    keyword: str
    description: str