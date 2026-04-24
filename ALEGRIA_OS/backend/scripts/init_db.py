import sqlite3
import os
from pathlib import Path

def init_db():
    db_path = Path("g:/ALEGRIA_OS/ALEGRIA_OS/ALEGRIA_OS/backend/prisma/dev.db")
    
    print(f"--- Iniciando reparacion de Base de Datos: {db_path} ---")
    
    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear tabla UserPreferences
    print("Creando tabla UserPreferences...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS UserPreferences (
        userId TEXT PRIMARY KEY,
        tonePreference TEXT DEFAULT 'balanced',
        responseLength TEXT DEFAULT 'medium',
        searchEnabled BOOLEAN DEFAULT 1,
        newsTopics TEXT,
        customRejections TEXT,
        updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Crear tabla FoundationalMemory
    print("Creando tabla FoundationalMemory...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS FoundationalMemory (
        key TEXT PRIMARY KEY,
        category TEXT,
        content TEXT,
        updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Crear tablas de Chat
    print("Creando tablas de Chat...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ChatSession (
        id TEXT PRIMARY KEY,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        metadata TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ChatMessage (
        id TEXT PRIMARY KEY,
        role TEXT,
        content TEXT,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        sessionId TEXT,
        msgType TEXT DEFAULT 'text',
        metadata TEXT,
        FOREIGN KEY (sessionId) REFERENCES ChatSession(id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Finalizado: Base de Datos inicializada correctamente.")

if __name__ == "__main__":
    init_db()
