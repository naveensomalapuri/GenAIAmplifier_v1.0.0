from pydantic import BaseModel

class Resume(BaseModel):
    client_problem: str
    generated_resume: dict
    client_name: str
