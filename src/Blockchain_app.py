import Blockchain
from uuid import uuid4
import socket
from flask import Flask, jsonify, request
from argparse import ArgumentParser
from threading import Thread, Semaphore
import requests
import time
import json
import platform
import os
#Semáforos
mutex = Semaphore(1)
# Instancia del nodo
app =Flask(__name__)

puerto = None

# Instanciacion de la aplicacion
blockchain =Blockchain.BlockChain()
nodos_red = set()

# Para saber mi ip
mi_ip = '192.168.56.1' 

@app.route('/transacciones/nueva', methods=['POST'])
def nueva_transaccion():
    values = request.get_json()
    # Comprobamos que todos los datos de la transaccion estan
    required =['origen', 'destino', 'cantidad']
    if not all(k in values for k in required):
        return 'Faltan valores', 400
    # Creamos una nueva transaccion
    indice =blockchain.nueva_transaccion(values['origen'], values['destino'],
    values['cantidad'])
    response ={'mensaje': f'La transaccion se incluira en el bloque con indice {indice}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def blockchain_completa():
    response = {
        # Solamente permitimos la cadena de aquellos bloques finales que tienen hash
        'chain': [b.toDict() for b in blockchain.chain if b.hash is not None],
        'longitud': len(blockchain.chain),
                    }
    print("Los nodos se han añadido a la red correctamente")
    return jsonify(response), 200

def copia_blockchain():
    global blockchain
    response = {
        'chain': [b.toDict() for b in blockchain.chain if b.hash is not None],
        'longitud': len(blockchain.chain),
        'date' : time.time()
    }
    return response
#COPIA DE SEGURIDAD
def copia_seguridad(puerto):
    while True:
        print("Realizando copia de seguridad")
        #Sección Crítica
        mutex.acquire()
        with open(f"respaldo-nodo{mi_ip}-{puerto}.json", "w") as archivo_json:
            json.dump(copia_blockchain(), archivo_json, indent=2)
        #Fin sección crítica
        mutex.release()
        print("Realizada copia de seguridad")
        time.sleep(60)


@app.route('/minar', methods=['GET'])
def minar():
    # No hay transacciones
    if len(blockchain.transacciones_no_confirmadas) ==0:
        response ={
        'mensaje': "No es posible crear un nuevo bloque. No hay transacciones"
        }
    else:
        # Hay transaccion, por lo tanto ademas de minar el bloque, recibimosrecompensa
        # Recibimos un pago por minar el bloque. Creamos una nueva transaccion con:
        # Dejamos como origen el 0
        # Destino nuestra ip
        # Cantidad = 1
        blockchain.nueva_transaccion("0", mi_ip, 1) #recompensa
        previous_hash =blockchain.chain[-1].hash 
        bloque = blockchain.nuevo_bloque(previous_hash)
        blockchain.prueba_trabajo(bloque)

        #RESOLVER CONFLICTOS
        conflicto = resuelve_conflictos()
        if conflicto:
            response = {
                'mensaje': "Ha habido un conflicto. Esta cadena se ha actualizado con una version mas larga"
            }
            #Obliga al nodo a capturar transacciones si quiere crear un nuevo bloque
        else:            
            blockchain.integrar_bloque(bloque, bloque.calcular_hash())
            response = {
                'mensaje' : "Nuevo bloque minado",
                'indice' : bloque.indice,
                'transacciones' : [transaccion.__dict__ for transaccion in bloque.transacciones],
                'prueba' : bloque.prueba,
                'hash_previo' : bloque.hash_previo,
                'hash' : bloque.hash,
                'timestramp' : bloque.timestamp
            }

    return jsonify(response), 200

@app.route('/sistema', methods=['GET'])
def get_system_details():
    system_details = {
        "maquina": platform.machine(),
        "nombre_sistema": platform.system(),
        "version": platform.version(),
        "procesador": platform.processor()
    }
    return jsonify(system_details)



#REGISTRAR NODOS (APLICACIÓN WEB DESCENTRALIZADA)
@app.route('/nodos/registrar', methods=['POST'])
def registrar_nodos_completo():
    values = request.get_json()
    global blockchain
    global nodos_red
    nodos_nuevos = values.get('direccion_nodos') #nodos_nuevos es una lista con las direcciones de cada nodo

    if nodos_nuevos is None:
        return "Error: No se ha proporcionado una lista de nodos", 400
    
    all_correct = True
    for nodo in nodos_nuevos:
        try:
            nodos_red.add(nodo)
            nodos_direcciones = [n for n in nodos_nuevos if n != nodo]
            nodos_direcciones.append(f"http://{mi_ip}:{puerto}")
            data = {
                'nodos_direcciones': nodos_direcciones, #lista de las direcciones de los otros nodos
                'blockchain': blockchain.copia()
                }                                           #El dumps lo pasa a formato str
            response = requests.post(nodo +"/nodos/registro_simple", data=json.dumps(data) , headers ={'Content-Type':"application/json"})
        except requests.exceptions.RequestException as e:
            all_correct = False
            print(f"Error al notificar el nodo {nodo}: {e}")

    if all_correct:
        response ={
        'mensaje': 'Se han incluido nuevos nodos en la red',
        'nodos_totales': list(nodos_red)
        }
    else:
        response = {
        'mensaje': 'Error notificando el nodo estipulado',
        }
    return jsonify(response), 201


def crear_blockchain(blockchain_recibida):

    """
    Construye la blockchain recibida bloque a bloque a partir del JSON recibido.
    Además, comprueba por cada bloque del blockchain del JSON, debde crear el bloque y comprobar que el hash es valido
    """
    blockchain_leida = Blockchain.BlockChain()
    #Añade el primer bloque
    b = blockchain_recibida[0]
    blockchain_leida.chain[0].hash = b.get("hash")
    blockchain_leida.chain[0].timestamp = b.get("timestamp")

    #Añade los demás bloques
    for b in blockchain_recibida[1:]:
        bloque = Blockchain.Bloque(
            indice= b.get("indice"), 
            transacciones = [Blockchain.Transaccion(**transaccion) for transaccion in b.get("transacciones")], 
            hash_previo = b.get("hash_previo"),  prueba = b.get("prueba"), timestamp = b.get("timestamp"),
            )
        
        blockchain_leida.integrar_bloque(bloque, bloque.calcular_hash())

    return blockchain_leida



@app.route('/nodos/registro_simple', methods=['POST'])
def registrar_nodo_actualiza_blockchain():

    """
    Recibe una lista con los otros nodos de la red y una copia en formato JSON del Blockchain del nodo principal
    """
    # Obtenemos la variable global de blockchain
    global blockchain
    global nodos_red
    read_json = request.get_json()
    nodes_addreses =read_json.get("nodos_direcciones") 
    for direccion in nodes_addreses:
        nodos_red.add(direccion)
    blockchain_recibida = read_json.get('blockchain')
    #Crear la cadena, blockchain_leida, a partir de la blockchain recibida en formato JSON
    blockchain_leida = crear_blockchain(blockchain_recibida)
    if blockchain_leida is None:
        return "El blockchain de la red esta currupto", 400
    else:
        blockchain = blockchain_leida
        return "La blockchain del nodo" + str(mi_ip) +":" +str(puerto) + "ha sido correctamente actualizada", 200

def resuelve_conflictos():
    """
    Mecanismo para establecer el consenso y resolver los conflictos.
    Tiene que haber una única cadena entre todos los nodos de la red, por lo que si un todo tiene una cadena
    más larga, todos los nodos deben de ser actualizados con la cadena más larga
    """
    global blockchain
    global nodos_red
    longitud_actual = len(blockchain.chain)
    conflicto = False
    for nodo in nodos_red:
        response = requests.get(str(nodo)+'/chain')
        response = response.json()
        cadena_nodo = response.get("chain")
        longitud_cadena_nodo = response.get("longitud")
        if longitud_cadena_nodo > longitud_actual: #la cadena del nodo es mayor es actu la cadena actual
            blockchain.chain = [Blockchain.Bloque(**{k: v for k, v in b.items() if k != 'hash'}) for b in cadena_nodo]
            for i, bloque in enumerate(blockchain.chain):
                bloque.hash = cadena_nodo[i]["hash"]
            #cambiamos la cadena actual por la más larga de la red
            conflicto = True #ha habido un conflicto (hay una cadena más larga que la del nodo actual)
    return conflicto

#PROTOCOLO ICMP
@app.route('/ping', methods=['POST'])
def ping():
    global nodos_red
    global puerto
    global mi_ip
    #url del nodo
    """
    Verifica que el nodo esté conectado a la red.
    Envía mensaje PING al nodo
    """
    todos_responden = True
    respuesta_final = ""
    for nodo in nodos_red:
        data = {

            "IP Host" : mi_ip,
            "puerto" : puerto,
            "mensaje" : "PING"
        }
        t0 = time.time()
        response = requests.post(nodo +"/pong", data=json.dumps(data) , headers ={'Content-Type':"application/json"}) #envía el mensaje al nodo
        tf = time.time()
        if response.status_code == 200: #el nodo ha recibido el mensaje
            respuesta = response.json()
            respuesta_final  += f"#{respuesta.get('mensaje')}"
            respuesta_final += f"Respuesta: {respuesta.get('respuesta')}"
            retardo = tf-t0
            respuesta_final += f"Retardo: {retardo}"
        else:
            todos_responden = False
    if todos_responden:
        respuesta_final += "#Todos los nodos responden"
    return jsonify({"respuesta_final": respuesta_final })
        
@app.route('/pong', methods=['POST'])
def pong():
    global mi_ip
    global puerto
    """
    El nodo responde al mensaje PING con un mensaje PONG
    """
    try:
        mensaje = request.get_json()
        response = {
            "IP nodo": mi_ip,
            "puerto" : puerto,
            "mensaje" : f"{mensaje.get('mensaje')} de {mensaje.get('IP Host')}: {mensaje.get('puerto')}",
            "respuesta": f"PONG{mi_ip}:{puerto}"

        }
        return jsonify(response), 200 #El nodo responde
    except requests.exceptions.RequestException as e:
        return jsonify({"Error" : e})

if __name__ == '__main__':
    parser =ArgumentParser()
    parser.add_argument('-p', '--puerto', default = 5001
                        , type=int, help='puerto para escuchar')
    args =parser.parse_args()
    puerto =args.puerto
    #hilo copia de seguridad
    hilo = Thread(target= copia_seguridad, args= (puerto,))
    hilo.start()
    app.run(host="0.0.0.0", port=puerto)
    hilo.join()
