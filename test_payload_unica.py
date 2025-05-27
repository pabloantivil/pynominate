import pymongo
import json
import numpy as np

def main():
    # Conexión a MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["quevotanEtiquetado"]
    
    votos_diputados = db["VotosDiputados"]
    parlamentarios = db["parlamentarios"]
    votaciones = db["votaciones"]
    new_wnominate = db["new_wnominate"]

    # ID de la votación a usar para esta prueba
    votacion_id_prueba = 37230

    # Inicializar el payload
    payload = {
        'votes': [],
        'memberwise': [],
        'idpt': {},
        'bp': {},
        'bw': {'b': 8.8633, 'w': 0.4619}
    }

    votos_por_diputado = {}

    # Obtener votos de la votación específica
    voto_doc = votos_diputados.find_one({"id": votacion_id_prueba})
    if not voto_doc:
        print(f"No se encontró la votación con id {votacion_id_prueba}")
        return

    detalle = voto_doc.get("detalle", {})

    votos = []
    
    # Obtener todos los diputados
    todos_diputados = list(parlamentarios.find({}))
    total_diputados = 0

    for diputado in todos_diputados:
        dip_id_str = str(diputado.get("id"))
        miembro = f"M{dip_id_str}"

        # Obtener voto desde detalle o asignar 2 (abstención/ausente)
        voto_original = detalle.get(dip_id_str, 2)
        voto_mapeado = mapear_voto(voto_original)
        votos.append((voto_mapeado, miembro))

        # Memberwise
        if miembro not in votos_por_diputado:
            votos_por_diputado[miembro] = []
        votos_por_diputado[miembro].append((voto_mapeado, f"V{votacion_id_prueba}"))

        # idpt en (0.0, 0.0)
        if miembro not in payload['idpt']:
            payload['idpt'][miembro] = [0.0, 0.0]
        
        total_diputados += 1

    # Estructura 'votes'
    payload['votes'].append({
        'id': f"V{votacion_id_prueba}",
        'update': True,
        'votes': votos
    })

    # Estructura 'bp'
    payload['bp'][f"V{votacion_id_prueba}"] = np.random.uniform(-0.1, 0.1, 4).tolist()
    #payload['bp'][f"V{votacion_id_prueba}"] = [0.0, 0.0, 0.1, 0.1]  # Placeholder para bp

    # Estructura 'memberwise'
    for member_id, votos in votos_por_diputado.items():
        payload['memberwise'].append({
            'icpsr': member_id,
            'update': True,
            'votes': votos
        })
        
    # idpt con coordenadas de new_wnominate
    """diputados_cursor = new_wnominate.find({"id": {"$in": [votacion_id_prueba]}})
    for doc in diputados_cursor:
        for dip in doc.get("diputados", []):
            member_id = f"M{dip['ID']}"
            if member_id not in payload['idpt']:
                payload['idpt'][member_id] = [dip.get('coordX', 0.0), dip.get('coordY', 0.0)]"""


    # Guardar en archivo JSON
    with open('payload_unica_votacion.json', 'w') as f:
        json.dump(payload, f, indent=2)

    print(f"✅ Payload guardado con {total_diputados} diputados en 'payload_unica_votacion.json' para la votación ID {votacion_id_prueba}")

def mapear_voto(valor):
    if valor == 1:
        return 1   # Sí
    elif valor == 0:
        return -1  # No
    elif valor == 2:
        return 0   # Abstención/Ausente
    else:
        return 0

if __name__ == "__main__":
    main()
