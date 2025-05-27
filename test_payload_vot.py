import pymongo
import json
import numpy as np

def main():
    votacion_objetivo_id = 37230  
    
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["quevotanEtiquetado"]
    votos_diputados = db["VotosDiputados"]
    parlamentarios = db["parlamentarios"]
    new_wnominate = db["new_wnominate"]
    votaciones = db["votaciones"]

    # Obtener parlamentarios
    todos_diputados = list(parlamentarios.find())

    # Buscar 30 votaciones centradas en la votación objetivo
    votaciones_lista = list(votaciones.find().sort("id", 1))  # Ordenadas por ID
    idx_centro = next(i for i, v in enumerate(votaciones_lista) if v["id"] == votacion_objetivo_id)
    idx_ini = max(0, idx_centro - 100)
    idx_fin = min(len(votaciones_lista), idx_centro + 100)
    votaciones_seleccionadas = votaciones_lista[idx_ini:idx_fin]
    votacion_ids = [v["id"] for v in votaciones_seleccionadas]

    # Inicializar estructuras
    payload = {
        'votes': [],
        'memberwise': [],
        'idpt': {},
        'bp': {},
        'bw': {'b': 8.8633, 'w': 0.4619}
    }

    votos_por_diputado = {}

    # Construcción del payload de votos
    for vot_id in votacion_ids:
        voto_doc = votos_diputados.find_one({"id": vot_id})
        if not voto_doc:
            continue

        detalle = voto_doc.get("detalle", {})
        votos = []

        for diputado in todos_diputados:
            dip_id_str = str(diputado.get("id"))
            miembro = f"M{dip_id_str}"

            voto_original = detalle.get(dip_id_str, 2)
            voto_mapeado = mapear_voto(voto_original)
            votos.append((voto_mapeado, miembro))

            if miembro not in votos_por_diputado:
                votos_por_diputado[miembro] = []
            votos_por_diputado[miembro].append((voto_mapeado, f"V{vot_id}"))

        payload['votes'].append({
            'id': f"V{vot_id}",
            'update': True,
            'votes': votos
        })

        # Generar valores bp aleatorios pequeños
        payload['bp'][f"V{vot_id}"] = np.random.uniform(-0.1, 0.1, 4).tolist()

    # Memberwise
    for member_id, votos in votos_por_diputado.items():
        payload['memberwise'].append({
            'icpsr': member_id,
            'update': True,
            'votes': votos
        })

    # Inicializar idpt 
    for diputado in todos_diputados:
        miembro = f"M{diputado['id']}"
        payload['idpt'][miembro] = [0.0, 0.0]  

    # Diputados de referencia
    doc_referencia = new_wnominate.find_one({"id": votacion_objetivo_id})
    if doc_referencia:
        extremos = sel_extremos(doc_referencia['diputados'])
        for dip in extremos:
            miembro = f"M{dip['ID']}"
            payload['idpt'][miembro] = [dip['coordX'], dip['coordY']]

    with open('payload_opcion2.json', 'w') as f:
        json.dump(payload, f, indent=2)

    print("Payload centrado en la votación", votacion_objetivo_id, "guardado en 'payload_opcion2.json'.")

def mapear_voto(valor):
    if valor == 1:
        return 1   # Sí
    elif valor == 0:
        return -1  # No
    elif valor == 2:
        return 0   # Abstención o Ausente
    else:
        return 0

def sel_extremos(diputados):
    izquierda = min(diputados, key=lambda x: x['coordX'])
    derecha = max(diputados, key=lambda x: x['coordX'])

    arriba = max(diputados, key=lambda x: x['coordY'])
    abajo  = min(diputados, key=lambda x: x['coordY'])

    return [izquierda, derecha, arriba, abajo]

if __name__ == "__main__":
    main()
