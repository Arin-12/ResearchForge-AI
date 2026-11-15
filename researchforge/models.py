from pydantic import BaseModel, Field
class Paper(BaseModel):
    title: str = ""
    authors: list[str] = Field(default_factory=list)
    summary: str = ""
    url: str = ""
    published: str = ""
