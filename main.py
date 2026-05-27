from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from datetime import datetime
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

client = MongoClient(os.environ["MONGO_URI"])
db = client["ISIS2304F29202610"]

@app.get("/")
def inicio():
    return {"estado": "API funcionando correctamente"}

# RF1 - Crear reseña
@app.post('/resenas')
def crear_resena(datos: dict = Body(...)):
    datos["fecha_creacion"] = datetime.utcnow()
    datos["estado"] = "publicada"
    datos["votos_utiles"] = []
    datos["destacada"] = False
    datos["respuesta_administrador"] = {}
    db["resenas"].insert_one(datos)
    return {'mensaje': 'Resena guardada'}

# RF2 - Editar reseña
@app.put('/resenas/{resena_id}')
def editar_resena(resena_id: str, datos: dict = Body(...)):
    db["resenas"].update_one(
        {"_id_oracle": resena_id},
        {"$set": {
            "calificacion": datos["calificacion"],
            "comentario": datos["comentario"]
        }}
    )
    return {'mensaje': 'Resena actualizada'}

# RF3 - Eliminar reseña (cliente)
@app.delete('/resenas/{resena_id}')
def eliminar_resena(resena_id: str):
    db["resenas"].update_one(
        {"_id_oracle": resena_id},
        {"$set": {"estado": "Eliminada"}}
    )
    return {'mensaje': 'Resena eliminada'}

# RF4 - Consultar reseñas de un hotel
@app.get('/hoteles/{hotel_id}/resenas')
def get_resenas_hotel(hotel_id: str):
    resenas = list(db["resenas"].find(
        {"hotel_id": hotel_id, "estado": "Publicada"},
        {"_id": 0}
    ).sort("fecha_creacion", -1))
    return resenas

# RF5 - Marcar como útil
@app.post('/resenas/{resena_id}/util')
def marcar_util(resena_id: str, datos: dict = Body(...)):
    db["resenas"].update_one(
        {"_id_oracle": resena_id},
        {"$inc": {"votos_utiles": 1},
         "$push": {"votos_utiles_lista": {
             "cliente_id": datos["cliente_id"],
             "fecha": datetime.now().isoformat()
         }}}
    )
    return {'mensaje': 'Voto registrado'}

# RF6 - Historial de reseñas de un cliente
@app.get('/clientes/{cliente_id}/resenas')
def get_resenas_cliente(cliente_id: str):
    resenas = list(db["resenas"].find(
        {"cliente_id": cliente_id},
        {"_id": 0}
    ).sort("fecha_creacion", -1))
    return resenas

# RF7 - Responder reseña (admin)
@app.put('/resenas/{resena_id}/respuesta')
def responder_resena(resena_id: str, datos: dict = Body(...)):
    db["resenas"].update_one(
        {"_id_oracle": resena_id},
        {"$set": {
            "respuesta_administrador": {
                "respuesta": datos["respuesta"],
                "fecha_respuesta": datetime.now().isoformat()
            }
        }}
    )
    return {'mensaje': 'Respuesta guardada'}

# RF8 - Eliminar reseña (admin)
@app.delete('/resenas/{resena_id}/admin')
def eliminar_resena_admin(resena_id: str):
    db["resenas"].update_one(
        {"_id_oracle": resena_id},
        {"$set": {"estado": "Eliminada"}}
    )
    return {'mensaje': 'Resena eliminada por admin'}

# RF9 - Destacar reseña
@app.put('/resenas/{resena_id}/destacar')
def destacar_resena(resena_id: str, datos: dict = Body(...)):
    db["resenas"].update_many(
        {"hotel_id": datos["hotel_id"]},
        {"$set": {"destacada": False}}
    )
    db["resenas"].update_one(
        {"_id_oracle": resena_id},
        {"$set": {"destacada": True}}
    )
    return {'mensaje': 'Resena destacada'}

