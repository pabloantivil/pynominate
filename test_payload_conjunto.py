import pymongo
import json
import numpy as np

def main():
    # Conexion a MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["quevotanEtiquetado"]

    votos_diputados = db["VotosDiputados"]
    parlamentarios = db["parlamentarios"]
    new_wnominate = db["new_wnominate"]
    votaciones = db["votaciones"]

    # Obtener todos los parlamentarios
    todos_diputados = list(parlamentarios.find())

    # Todas las votaciones
    votaciones_cursor = votaciones.find().sort("id", -1)
    votaciones_list = list(votaciones_cursor)
    votacion_ids = [v["id"] for v in votaciones_list]

    # Inicializar estructuras
    payload = {
        'votes': [],
        'memberwise': [],
        'idpt': {},
        'bp': {},
        'bw': {'b': 8.8633, 'w': 0.4619}
    }

    votos_por_diputado = {}

    for vot_id in votacion_ids:
        voto_doc = votos_diputados.find_one({"id": vot_id})
        if not voto_doc:
            continue

        detalle = voto_doc.get("detalle", {})
        votos = []

        for diputado in todos_diputados:
            dip_id_str = str(diputado.get("id"))
            miembro = f"M{dip_id_str}"

            # Obtener el voto si existe; si no, abstención/ausente (2)
            voto_original = detalle.get(dip_id_str, 2)
            voto_mapeado = mapear_voto(voto_original)
            votos.append((voto_mapeado, miembro))

            # Agregar a memberwise
            if miembro not in votos_por_diputado:
                votos_por_diputado[miembro] = []
            votos_por_diputado[miembro].append((voto_mapeado, f"V{vot_id}"))

            # Inicializar idpt si aún no está
            if miembro not in payload['idpt']:
                payload['idpt'][miembro] = [0.0, 0.0]

        # Agregar votación al payload
        payload['votes'].append({
            'id': f"V{vot_id}",
            'update': True,
            'votes': votos
        })

        # bp provisional
        #payload['bp'][f"V{vot_id}"] = np.random.uniform(-0.1, 0.1, 4).tolist() # Generar coordenadas aleatorias 
        payload['bp'][f"V{vot_id}"] = [0.0, 0.0, 0.1, 0.1]  # Placeholder

    # Construir memberwise
    for member_id, votos in votos_por_diputado.items():
        payload['memberwise'].append({
            'icpsr': member_id,
            'update': True,
            'votes': votos
        })
    
    # Construir idpt usando new_wnominate
    """diputados_cursor = new_wnominate.find({"id": {"$in": votacion_ids}})
    for doc in diputados_cursor:
        for dip in doc.get("diputados", []):
            member_id = f"M{dip['ID']}"
            if member_id not in payload['idpt']:
                payload['idpt'][member_id] = [dip.get('coordX', 0.0), dip.get('coordY', 0.0)]"""

    # Guardar el payload
    with open('payload_conjunto.json', 'w') as f:
        json.dump(payload, f, indent=2)

    print("✅ Payload guardado en 'payload_conjunto.json' con todos los diputados incluidos.")

def mapear_voto(valor):
    if valor == 1:
        return 1   # Sí
    elif valor == 0:
        return -1  # No
    elif valor == 2:
        return 0   # Abstención o Ausente
    else:
        return 0

if __name__ == "__main__":
    main()
