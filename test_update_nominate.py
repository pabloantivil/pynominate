#!/usr/bin/env python
import sys
import numpy as np
from pymongo import MongoClient

# Agrega el path raíz del repo
sys.path.append('.')

from pynominate.nominate import update_nominate

# --- Conexión a MongoDB ---
client = MongoClient("mongodb://localhost:27017/")  
db = client["quevotanEtiquetado"]          
votos_coll = db["VotosDiputados"]
parl_coll = db["parlamentarios"]

# --- Obtener el documento de interés ---
voto_doc = votos_coll.find_one({"id": 37270})
if not voto_doc:
    raise ValueError("No se encontró el documento con id 37270 en VotosDiputados.")

vote_id = str(voto_doc["id"])
detalle = voto_doc["detalle"]  # Diccionario: {diputado_id: voto}

# --- Generar idpt desde Parlamentarios ---
idpt = {}
for diputado_id in detalle:
    dip_id = int(diputado_id)
    parlam = parl_coll.find_one({"id": dip_id})
    if parlam:
        # Puedes ajustar este vector si tienes valores reales
        idpt[str(diputado_id)] = np.random.uniform(-1, 1, size=2).tolist()
    else:
        print(f"Parlamentario {diputado_id} no encontrado.")

# --- Formatear votes y memberwise ---
votes_formatted = []
memberwise = []

for diputado_id_str, voto in detalle.items():
    if diputado_id_str not in idpt:
        print(f"Diputado {diputado_id_str} ignorado porque no tiene vector en idpt.")
        continue  # Saltar este diputado

    vote_value = 1 if voto == 1 else -1 if voto == 0 else 0
    votes_formatted.append((vote_value, diputado_id_str))
    memberwise.append({
        "icpsr": diputado_id_str,
        "update": True,
        "votes": [(vote_value, vote_id)]
    })

# --- Crear payload final ---
payload = {
    "votes": [
        {
            "id": vote_id,
            "update": True,
            "votes": votes_formatted
        }
    ],
    "memberwise": memberwise,
    "idpt": {k: np.array(v) for k, v in idpt.items()},
    "bp": {
        vote_id: np.array([0.0, 0.0, 0.1, 0.1])
    },
    "bw": {
        "b": 9.0,
        "w": 0.5
    }
}

# --- Ejecutar update_nominate ---
if __name__ == "__main__":
    result = update_nominate(
        payload,
        maxiter=1,
        cores=1,
        update=["bp", "idpt", "bw"],
        xtol=1e-4,
        add_meta=[]
    )
    print("Resultado de update_nominate con datos reales:")
    print(result)
