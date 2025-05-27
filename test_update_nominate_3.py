#!/usr/bin/env python
from pynominate.nominate import update_nominate
import sys
import json
import numpy as np

sys.path.append('.')


with open("payload_conjunto.json", "r", encoding="utf-8") as f:
    raw_payload = json.load(f)

# Convertir listas en numpy arrays (solo donde es necesario)
# update_nominate espera np.array en "idpt" y "bp", no listas comunes
payload = {
    "votes": raw_payload["votes"],
    "memberwise": raw_payload["memberwise"],
    "idpt": {k: np.array(v) for k, v in raw_payload["idpt"].items()},
    "bp": {k: np.array(v) for k, v in raw_payload["bp"].items()},
    "bw": {
        "b": float(raw_payload["bw"]["b"]),
        "w": float(raw_payload["bw"]["w"])
    }
}

# Ejecutar update_nominate
if __name__ == "__main__":
    result = update_nominate(
        payload,
        maxiter=30,
        cores=1,
        update=["bp", "idpt", "bw"],
        xtol=1e-4,
        add_meta=[]
    )
    print("Resultado de update_nominate:")
    print(result)
    
