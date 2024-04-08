from pydantic import BaseModel


class SendMessageDTO(BaseModel):
    content: str


class ResponseDTO(BaseModel):
    message: str


class BCMessageDTO(BaseModel):
    id: str
    content: str
