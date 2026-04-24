const textoAAudio = async (texto) => {
  try {
    // Configuración de la API para convertir texto a audio
    const apiEndpoint = 'http://localhost:5000/text-to-speech';
    const respuesta = await fetch(apiEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ texto }),
    });

    // Verificar si la respuesta es exitosa
    if (!respuesta.ok) {
      throw new Error(`Error al convertir texto a audio: ${respuesta.status}`);
    }

    // Obtener el archivo de audio generado
    const archivoAudio = await respuesta.blob();
    return archivoAudio;
  } catch (error) {
    console.error('Error al convertir texto a audio:', error);
    throw error;
  }
};

const descargarAudio = (archivoAudio) => {
  try {
    // Crear un enlace para descargar el archivo de audio
    const enlaceDescarga = document.createElement('a');
    enlaceDescarga.href = URL.createObjectURL(archivoAudio);
    enlaceDescarga.download = 'audio.mp3';
    enlaceDescarga.click();
  } catch (error) {
    console.error('Error al descargar audio:', error);
  }
};

const validarTexto = (texto) => {
  // Verificar si el texto no está vacío
  if (!texto.trim()) {
    throw new Error('Por favor, ingrese texto para convertir a audio');
  }
};

const eventoConvertirTextoAAudio = async () => {
  try {
    // Obtener el texto ingresado por el usuario
    const texto = document.getElementById('texto').value;

    // Validar el texto ingresado
    validarTexto(texto);

    // Convertir el texto a audio
    const archivoAudio = await textoAAudio(texto);

    // Descargar el audio generado
    descargarAudio(archivoAudio);
  } catch (error) {
    console.error('Error al convertir texto a audio:', error);
    alert('Error al convertir texto a audio: ' + error.message);
  }
};

// Agregar evento de click al botón de convertir texto a audio
document.getElementById('convertir').addEventListener('click', eventoConvertirTextoAAudio);