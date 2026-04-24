import os
import uuid
import datetime

def generate_unique_filename(extension):
    """
    Genera un nombre de archivo único con la extensión dada.
    
    Args:
        extension (str): La extensión del archivo (por ejemplo, 'mp3', 'txt', etc.)
    
    Returns:
        str: El nombre de archivo único generado
    """
    try:
        unique_id = str(uuid.uuid4())
        filename = f"{unique_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.{extension}"
        return filename
    except Exception as e:
        print(f"Error generando nombre de archivo único: {str(e)}")
        return None

def get_file_extension(filename):
    """
    Obtiene la extensión de un archivo a partir de su nombre.
    
    Args:
        filename (str): El nombre del archivo
    
    Returns:
        str: La extensión del archivo (por ejemplo, 'mp3', 'txt', etc.)
    """
    try:
        file_extension = os.path.splitext(filename)[1][1:]
        return file_extension
    except Exception as e:
        print(f"Error obteniendo extensión de archivo: {str(e)}")
        return None

def create_directory(directory_path):
    """
    Crea un directorio si no existe.
    
    Args:
        directory_path (str): La ruta del directorio a crear
    
    Returns:
        bool: True si el directorio se creó con éxito, False de lo contrario
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        return True
    except Exception as e:
        print(f"Error creando directorio: {str(e)}")
        return False

def delete_file(filename):
    """
    Elimina un archivo.
    
    Args:
        filename (str): La ruta del archivo a eliminar
    
    Returns:
        bool: True si el archivo se eliminó con éxito, False de lo contrario
    """
    try:
        if os.path.exists(filename):
            os.remove(filename)
        return True
    except Exception as e:
        print(f"Error eliminando archivo: {str(e)}")
        return False