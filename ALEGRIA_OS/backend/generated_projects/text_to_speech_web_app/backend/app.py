from flask import Flask, request, jsonify, send_file
from text_to_speech import text_to_speech
from utils import generate_unique_filename
import logging
import os

app = Flask(__name__)

# Configuración del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ruta para la conversión de texto a audio
@app.route('/convert', methods=['POST'])
def convert_text_to_speech():
    try:
        # Obtiene el texto del cuerpo de la solicitud
        data = request.json
        text = data.get('text')

        # Verifica si el texto es válido
        if not text:
            return jsonify({'error': 'Texto no proporcionado'}), 400

        # Genera un nombre de archivo único para el audio
        filename = generate_unique_filename()

        # Convierte el texto a audio utilizando la biblioteca gTTS
        audio_path = text_to_speech(text, filename)

        # Envía el archivo de audio como respuesta
        return send_file(audio_path, as_attachment=True, attachment_filename=filename)

    except Exception as e:
        # Registra el error y devuelve una respuesta de error
        logger.error(f'Error al convertir texto a audio: {str(e)}')
        return jsonify({'error': 'Error al convertir texto a audio'}), 500

# Ruta para la raíz de la aplicación
@app.route('/')
def index():
    return 'Aplicación de conversión de texto a audio'

# Inicia la aplicación
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)