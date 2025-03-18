# Proyecto Blockchain

## Autores
- Jorge Ibinarriaga Robles

## Descripción del Proyecto
Este proyecto consiste en una implementación básica de una cadena de bloques (Blockchain) mediante una aplicación descentralizada compuesta por nodos conectados en red.

El objetivo principal es desarrollar un sistema funcional que permita realizar transacciones seguras y verificar su integridad a través de la minería de bloques.

## Estructura del Proyecto

### Librerías Principales:

- **Blockchain.py**
  - Gestiona la creación y validación del objeto Blockchain, bloques y transacciones.
  - Realiza cálculos de hash y prueba de trabajo.
  
- **Blockchain_app.py**
  - Implementa la red descentralizada utilizando Flask.
  - Gestiona la comunicación entre nodos a través de peticiones HTTP.
  - Realiza copias de seguridad periódicas en formato JSON.

### Funcionalidades Principales:

- **Transacciones:** Se crean y almacenan para posteriormente añadirse a bloques.
- **Bloques:** Cada bloque contiene transacciones y se valida mediante un hash único.
- **Minería:** Implementa un algoritmo de prueba de trabajo para validar y añadir bloques a la cadena.
- **Red Descentralizada:** Los nodos se comunican y sincronizan automáticamente para mantener una única versión actualizada del Blockchain.
- **Copia de Seguridad:** Automatiza la generación periódica de copias de seguridad de la cadena.

### Requisitos del Sistema
- Python 3.x
- Flask
- Librería requests

### Instalación

1. Clona el repositorio:
   ```bash
   git clone [URL_REPOSITORIO]
   ```

2. Instala las dependencias:
   ```bash
   pip install flask requests
   ```

3. Ejecuta el programa:
   ```bash
   python Blockchain_app.py
   ```

### Uso

- **Añadir nodos a la red:** Envía una petición POST con el JSON correspondiente.
- **Consultar la cadena actual:** Usa la ruta `/chain`.
- **Realizar transacciones:** Envía peticiones POST con los datos de la transacción en formato JSON.
- **Minar bloques:** Realiza una petición específica para minar, obteniendo recompensas por el trabajo realizado.

### Pruebas

El archivo `Request.py` automatiza las pruebas para asegurar la correcta integración y funcionalidad de la aplicación.

Para probar en máquinas virtuales, consulta la documentación específica dentro del archivo proporcionado en este repositorio.

### Contribuir

Las contribuciones son bienvenidas. Cualquier mejora o corrección puede ser enviada mediante un Pull Request.



