"""
Las transacciones de nuestra aplicación, en formato JSON, se almacenarán en bloques.
Cada transacción (bloque) tenndrá un identificador único
"""
from typing import List
import json
import time
from datetime import datetime
import hashlib
class Transaccion:
    def __init__(self, origen, destino, cantidad, timestamp):
        self.origen = origen
        self.destino = destino
        self.cantidad = cantidad
        self.timestamp = timestamp
    def __str__(self):
        return f"""
        Origen: {self.origen}
        Destino: {self.destino}
        Cantidad: {self.cantidad}
        Timestamp: {self.timestamp}
        """
    def to_dict(self):
        return {
            "origen": self.origen,
            "destino": self.destino,
            "cantidad": self.cantidad,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str) #pasa el Json a diccionario 
        return cls(**data) #desempaquetar diccionarios y usa los argumentos del diccionario como atributos

class Bloque:
    def __init__(self, indice:int, transacciones: List,
                 hash_previo:str, prueba: int = 0, timestamp = time.time()):
        """
        Constructor de la clase 'bloque'.
        Parámetros:
        -Indice: ID único de nuestro bloque
        -Transacciones: lista con todas las transacciones.
        -Timestamp: momento en el que el bloque fue generado.
        -hash_previo: clave criptográfica del anterior bloque 
        (bloques encadenados uno detrás del otro)
        El hash del bloque inicializado es None.
        -param_prueba: prueba de trabajo
        """
        self.indice = indice
        self.transacciones = transacciones
        self.timestamp = timestamp
        self.hash_previo = hash_previo
        self.prueba = prueba
        self.hash = None
    

    def calcular_hash(self):
        """
        Devuelve el hash de un bloque
        """
        diccionario = dict()
        diccionario["indice"] = self.indice
        diccionario["timestamp"] = self.timestamp
        diccionario["hash_previo"] = self.hash_previo
        diccionario["prueba"] = self.prueba
        diccionario["hash"] = self.hash
        diccionario["transacciones"] = []
        for transaccion in self.transacciones:
            if type(transaccion) == dict:
                diccionario["transacciones"].append(transaccion)
            else:
                diccionario["transacciones"].append(transaccion.to_dict())
        block_string = json.dumps(diccionario, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    def toDict(self):  
        lista = []
        for transaccion in self.transacciones:
            if type(transaccion) == dict:
                lista.append(transaccion)
            else:
                lista.append(transaccion.__dict__)      
        return {
            "indice" : self.indice,
            "transacciones" :lista,
            "timestamp" : self.timestamp,
            "hash_previo" : self.hash_previo,
            "prueba" : self.prueba,
            "hash" : self.hash
        }
    def __str__(self):
        return f"""
        Indice: {self.indice}
        Transacciones: 
        {[(t.origen, t.destino, t.cantidad, t.timestamp) for t in self.transacciones]}
        timestamp: {self.timestamp}
        hash_previo: {self.hash_previo}
        prueba: {self.prueba}
        hash: {self.hash}
        """
    
class  BlockChain():
    """
    Lista de bloques.
    """
    def __init__(self):
        self.dificultad = 4
        self.transacciones_no_confirmadas = []
        self.chain = []
        self.primer_bloque()
    def primer_bloque(self):
        bloque = Bloque(indice = 1, transacciones=[], hash_previo = "1") 
        bloque.hash = bloque.calcular_hash()
        self.chain.append(bloque)
    def nuevo_bloque(self, hash_previo: str) ->Bloque:
        """
        Crea un nuevo bloque a partir de las transacciones que no estan
        confirmadas
        :param hash_previo: el hash del bloque anterior de la cadena
        :return: el nuevo bloque
        """
        indice = len(self.chain) + 1
        bloque = Bloque(indice,self.transacciones_no_confirmadas, hash_previo) #ahora las transacciones están confirmadas
        return bloque

    def nueva_transaccion(self, origen:str, destino:str, cantidad: float) -> int:
        """
        Crea una nueva transaccion a partir de un origen, un destino y una 
        cantidad y la incluye en las listas de transacciones.
        Devuelve el indice del bloque que va a almacenar la transacción
        """
        timestramp = time.time() #momento en el que se añade la transacción
        transaccion = Transaccion(origen, destino, cantidad, timestramp)
        self.transacciones_no_confirmadas.append(transaccion)
        return len(self.chain) + 1
    
    def prueba_trabajo(self, bloque: Bloque) ->str:
        """
        Algoritmo simple de prueba de trabajo:
        - Calculara el hash del bloque hasta que encuentre un hash que empiece
        por tantos ceros como dificultad.
        - Cada vez que el bloque obtenga un hash que no sea adecuado,
        incrementara en uno el campo de ''prueba'' del bloque
        :param bloque: objeto de tipo bloque
        :return: el hash del nuevo bloque (dejara el campo de hash del bloque sin
        modificar)
        """
        #
        hash = bloque.calcular_hash()
        while hash[:self.dificultad] != "0"*self.dificultad:  #el hash no empieza por 0000
            bloque.prueba += 1 #numero de veces que ha habido que calcular el hash para cumplir la restricción de ceros
            hash = bloque.calcular_hash() #recalcula el hash
        return hash
    
    def prueba_valida(self, bloque: Bloque, hash_bloque: str) ->bool:
        """
        Metodo que comprueba si el hash_bloque comienza con tantos ceros como la
        dificultad estipulada en el blockchain
        Ademas comprobara que hash_bloque coincide con el valor devuelvo del
        metodo de calcular hash del bloque.
        Si cualquiera de ambas comprobaciones es falsa, devolvera falso y en caso
        contrario, verdarero
        :param bloque:
        :param hash_bloque:
        :return:
        """
        return (hash_bloque[:self.dificultad] == "0" * self.dificultad) & (hash_bloque == bloque.calcular_hash())

    def integrar_bloque(self, bloque_nuevo: Bloque, hash_prueba: str) ->bool:
        
        """
        Metodo para integrar correctamente un bloque a la cadena de bloques.
        Debe comprobar que hash_prueba es valida y que el hash del bloque ultimo
        de la cadena coincida con el hash_previo del bloque que se va a integrar. 

        Si pasa las comprobaciones, actualiza el hash del bloque nuevo a integrar con hash_prueba, 
        lo inserta en la cadena y hace un reset de las transacciones no confirmadas (
        vuelve a dejar la lista de transacciones no confirmadas a una lista vacia)
        :param bloque_nuevo: el nuevo bloque que se va a integrar
        :param hash_prueba: la prueba de hash
        :return: True si se ha podido ejecutar bien y False en caso contrario (si
        no ha pasado alguna prueba)
        """
        if (self.prueba_valida(bloque_nuevo, hash_prueba)) & (self.chain[-1].hash == bloque_nuevo.hash_previo):
            print(f"Se ha añadido el bloque {bloque_nuevo.indice} correctamente")
            bloque_nuevo.hash = hash_prueba
            self.chain.append(bloque_nuevo)
            self.transacciones_no_confirmadas = [] #resetea las transacciones al haber añadido el bloque
            return True
        else:
            return False


    def copia(self):
        return [b.toDict() for b in self.chain if b.hash is not None]

