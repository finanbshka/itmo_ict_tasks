from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import asyncpg
import uvicorn

app = FastAPI()

DATABASE_URL = "postgresql://user:password@localhost/namedb"








async def get_db_connection():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

class UserAuthMe(BaseModel):
    username: str
    password: str

class UserAuthMessage(BaseModel):
    username: str
    password: str
    message: dict


@app.post("/me")
async def create_user(auth: UserAuthMe, db=Depends(get_db_connection)):
    try:
        query = """
        INSERT INTO users (username, password) VALUES ($1, $2) RETURNING id, username
        """
        user = await db.fetchrow(query, auth.username, auth.password)
        return {"id": user["id"], "username": user["username"]}
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Username already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/message")
async def create_message(auth: UserAuthMessage, db=Depends(get_db_connection)):
    # Получаем id отправителя и получателя
    query_sender = "SELECT id FROM users WHERE username = $1 AND password = $2"
    sender = await db.fetchrow(query_sender, auth.username, auth.password)

    if not sender:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    query_receiver = "SELECT id FROM users WHERE username = $1"
    receiver = await db.fetchrow(query_receiver, auth.message["to"])

    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
        # Вставляем сообщение
    query_message = """
    INSERT INTO messages ("from", "to", text) 
    VALUES ($1, $2, $3) 
    RETURNING id
    """
    message = await db.fetchrow(query_message, sender["id"], receiver["id"], auth.message["text"])

    if not message:
        raise HTTPException(status_code=500, detail="Message creation failed")

    return {"message_id": message["id"]}


if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=7222)
