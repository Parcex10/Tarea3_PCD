from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStrField
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()


models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# Modelo de datos para un usuario
class User(BaseModel):
    user_name: str
    user_id: str
    user_email: EmailStr
    age: Optional[int] = None
    recommendations: List[str]
    ZIP: Optional[str] = None


# Endpoint para crear un usuario
@app.post("/users/")
def create_user(user: User):
    # Verificar si el correo ya existe en la base de datos
    if any(u['user_email'] == user.user_email for u in db):
        raise HTTPException(status_code=400, detail="El email ya existe")

    # Generar un id único si no se provee
    if not user.user_id:
        user.user_id = str(uuid4())

    db.append(user.dict())
    return {"message": "Usuario creado exitosamente", "user": user}


# Endpoint para actualizar un usuario por id
@app.put("/users/{user_id}")
def update_user(user_id: str, updated_user: User):
    for user in db:
        if user['user_id'] == user_id:
            user.update(updated_user(exclude_unset=True))
            return {"message": "Usuario actualizado exitosamente", "user": user}

    raise HTTPException(status_code=404, detail="Usuario no encontrado")


# Endpoint para obtener la información de un usuario por id
@app.get("/users/{user_id}")
def get_user(user_id: str):
    for user in db:
        if user['user_id'] == user_id:
            return user

    raise HTTPException(status_code=404, detail="Usuario no encontrado")


# Endpoint para eliminar un usuario por id
@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    for user in db:
        if user['user_id'] == user_id:
            db.remove(user)
            return {"message": "Usuario eliminado exitosamente"}

    raise HTTPException(status_code=404, detail="Usuario no encontrado")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)