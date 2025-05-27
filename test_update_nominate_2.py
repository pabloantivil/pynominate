#!/usr/bin/env python
import sys
import numpy as np

# Asegúrate de ejecutar esto desde la carpeta raíz del repositorio
sys.path.append('.')  

from pynominate.nominate import update_nominate

# --- Payload de prueba ---
payload = {
    'votes': [
        {
            'id': 'V1',
            'update': True,
            'votes': [
                (1,  'M1'),   # Miembro M1 votó "sí"
                (-1, 'M2')    # Miembro M2 votó "no"
            ]
        }
    ],
    'memberwise': [
        {
            'icpsr': 'M1',
            'update': True,
            'votes': [(1, 'V1')]
        },
        {
            'icpsr': 'M2',
            'update': True,
            'votes': [(-1, 'V1')]
        }
    ],
    'idpt': {
        'M1': np.array([ 0.1,  0.2]),
        'M2': np.array([-0.1, -0.3])
    },
    'bp': {
        'V1': np.array([0.0, 0.0, 0.1, 0.1])
    },
    'bw': {
        'b': 9.0,
        'w': 0.5
    }
}

# --- Ejecución de prueba ---
if __name__ == '__main__':
    result = update_nominate(
        payload,
        maxiter=1,                  # 1 iteración para prueba
        cores=1,                    # 1 proceso
        update=['bp', 'idpt', 'bw'],# actualizar parámetros bp, idpt y bw
        xtol=1e-4,
        add_meta=[]                 # sin agregar metadatos extra
    )
    print("Resultado de update_nominate con payload de prueba:")
    print(result)
