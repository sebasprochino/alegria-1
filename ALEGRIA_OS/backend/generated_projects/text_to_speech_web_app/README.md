# Text to Speech Web App
==========================

## Descripción del Proyecto
---------------------------

La aplicación web "Text to Speech" convierte texto a audio en formato MP3. Esta aplicación utiliza la biblioteca gTTS (Google Text-to-Speech) para generar el audio. La aplicación tiene una interfaz de usuario básica que permite a los usuarios ingresar texto y descargar el audio generado.

## Instalación
--------------

Para instalar y ejecutar la aplicación, sigue los siguientes pasos:

1. **Instalar dependencias**: La aplicación requiere las siguientes dependencias:
	* Python: `flask`, `gtts`, `pydub`
	* JavaScript: `jquery`
2. **Instalar Python**: Asegúrate de tener Python instalado en tu sistema.
3. **Instalar dependencias de Python**: Ejecuta el comando `pip install -r requirements.txt` en la terminal.
4. **Iniciar la aplicación**: Ejecuta el comando `python app.py` en la terminal.

## Uso
-----

Para utilizar la aplicación, sigue los siguientes pasos:

1. **Iniciar la aplicación**: Abre un navegador y ve a `http://localhost:5000`.
2. **Ingresar texto**: Ingresa el texto que deseas convertir a audio en el campo de texto.
3. **Descargar audio**: Haz clic en el botón "Descargar audio" para descargar el audio generado.

## Estructura del Proyecto
-------------------------

La aplicación tiene la siguiente estructura:

* **Backend**:
	+ `app.py`: Archivo principal del backend, maneja las solicitudes y respuestas de la aplicación.
	+ `text_to_speech.py`: Archivo que contiene la lógica para convertir texto a audio utilizando la biblioteca gTTS.
	+ `utils.py`: Archivo que contiene funciones útiles para la aplicación, como la generación de nombres de archivo únicos.
* **Frontend**:
	+ `index.html`: Archivo HTML que contiene la interfaz de usuario de la aplicación.
	+ `styles.css`: Archivo CSS que contiene los estilos para la interfaz de usuario.
	+ `app.js`: Archivo JavaScript que contiene la lógica del frontend de la aplicación.
* **Config**:
	+ `requirements.txt`: Archivo que contiene las dependencias necesarias para la aplicación.
	+ `README.md`: Archivo que contiene información sobre la aplicación y cómo ejecutarla.

## API Endpoints
----------------

La aplicación tiene los siguientes endpoints:

* **GET /**: Retorna la interfaz de usuario de la aplicación.
* **POST /text_to_speech**: Convierte el texto ingresado a audio y devuelve el archivo de audio generado.

### Ejemplo de Uso

Para convertir texto a audio, envía un POST request a `http://localhost:5000/text_to_speech` con el texto en el cuerpo de la solicitud:
```bash
curl -X POST -H "Content-Type: text/plain" -d "Hola, mundo" http://localhost:5000/text_to_speech
```
La aplicación devuelve el archivo de audio generado en formato MP3.

## Características
------------------

La aplicación tiene las siguientes características:

* **Conversión de texto a audio**: La aplicación convierte texto a audio en formato MP3 utilizando la biblioteca gTTS.
* **Interfaz de usuario básica**: La aplicación tiene una interfaz de usuario básica que permite a los usuarios ingresar texto y descargar el audio generado.