class TextToSpeech:
    def __init__(self, texto):
        self.texto = texto

    def convertir_texto_a_audio(self):
        try:
            from gtts import gTTS
            import os
            audio = gTTS(text=self.texto, lang='es')
            audio.save("audio.mp3")
            return True
        except Exception as e:
            print(f"Error al convertir texto a audio: {e}")
            return False

    def guardar_audio(self, nombre_archivo):
        try:
            import os
            os.rename("audio.mp3", nombre_archivo)
            return True
        except Exception as e:
            print(f"Error al guardar audio: {e}")
            return False

def main():
    texto = "Hola, este es un ejemplo de texto a audio"
    tts = TextToSpeech(texto)
    if tts.convertir_texto_a_audio():
        print("Texto convertido a audio con éxito")
        nombre_archivo = "audio_generado.mp3"
        if tts.guardar_audio(nombre_archivo):
            print(f"Audio guardado con éxito en {nombre_archivo}")
        else:
            print("Error al guardar audio")
    else:
        print("Error al convertir texto a audio")

if __name__ == "__main__":
    main()