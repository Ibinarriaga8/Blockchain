import requests
import json
# Cabecera JSON (comun a todas)
cabecera ={'Content-type': 'application/json', 'Accept': 'text/plain'}
# datos transaccion
transaccion_nueva ={'origen': 'nodoA', 'destino': 'nodoB', 'cantidad': 10}
r =requests.post('http://127.0.0.1:5000/transacciones/nueva', data =json.dumps(
transaccion_nueva), headers=cabecera)
print(r.text)
#MINAR
r =requests.get('http://127.0.0.1:5000/minar')
print(r.text)
r =requests.get('http://127.0.0.1:5000/chain')
print(r.text)
#AÑADIR NODOS
nodos_nuevos = {"direccion_nodos":["http://127.0.0.1:5001"]}
r = requests.post('http://127.0.0.1:5000/nodos/registrar', data = json.dumps(nodos_nuevos), headers=cabecera)
print(r.text)
#Comprobamos conexión (ICMP)
r = requests.post('http://127.0.0.1:5000/ping')
print(r.text)
#Detalles del sistema
r = requests.get('http://127.0.0.1:5001/sistema')
print(r.text)
#Comprobamos que tengan la misma cadena:
r =requests.get('http://127.0.0.1:5000/minar')
print(f"Cadena nodo 5000: {r.text}")
r =requests.get('http://127.0.0.1:5001/minar')
print(f"Cadena nodo 5001: {r.text}")
#Minamos nodo 5000
transaccion_nueva ={'origen': 'nodoC', 'destino': 'nodoD', 'cantidad': 2}
r =requests.post('http://127.0.0.1:5000/transacciones/nueva', data =json.dumps(
transaccion_nueva), headers=cabecera)
print(r.text)
r =requests.get('http://127.0.0.1:5000/minar')
print(r.text)
#Intentamos minar nodo 5001
transaccion_nueva ={'origen': 'nodoC', 'destino': 'nodoD', 'cantidad': 2}
r =requests.post('http://127.0.0.1:5001/transacciones/nueva', data =json.dumps(
transaccion_nueva), headers=cabecera)
print(r.text)
r =requests.get('http://127.0.0.1:5001/minar')
print(r.text)