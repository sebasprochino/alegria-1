from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ALEGR-IA CORE")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    content: str

MEMORY = []

@app.post("/chat")
def chat(msg: Message):
    MEMORY.append({"role": "user", "content": msg.content})

    response = {
        "role": "anima",
        "content": f"Anima Chordata responde: {msg.content}"
    }

    MEMORY.append(response)
    return response

@app.get("/memory")
def memory():
    return MEMORY
