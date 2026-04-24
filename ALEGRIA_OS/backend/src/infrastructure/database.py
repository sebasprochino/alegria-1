import sqlite3
import json
import logging
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger("ALEGRIA_DB")

class Database:
    """
    Motor de persistencia soberano (SQLite).
    Soporta operaciones asíncronas básicas envolviendo sqlite3.
    """
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            # backend/data/alegria.db
            self.db_path = Path(__file__).resolve().parents[2] / "data" / "alegria.db"
        else:
            self.db_path = db_path
            
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"🗄️ [DB] Conectado a: {self.db_path}")

    def _init_db(self):
        """Inicializa las tablas base si no existen."""
        with sqlite3.connect(self.db_path, timeout=30.0) as conn:
            cursor = conn.cursor()
            
            # Habilitar modo WAL para mejor concurrencia (lectores no bloquean escritores)
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            
            # Tabla de Auditoría Cognitiva (Timeline)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    intention_id TEXT,
                    stage TEXT,
                    timestamp REAL,
                    agent TEXT,
                    data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Índices para búsqueda rápida por intención
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_intention ON audit_log(intention_id)")
            
            conn.commit()

    async def insert(self, table: str, data: Dict[str, Any]):
        """Inserta un registro de forma no bloqueante con reintentos."""
        max_retries = 5
        for i in range(max_retries):
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._insert_sync, table, data)
                return
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() and i < max_retries - 1:
                    wait_time = (i + 1) * 0.5
                    logger.warning(f"⚠️ [DB] Base de datos bloqueada. Reintentando en {wait_time}s... (Intento {i+1})")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"❌ [DB] Error en insert: {e}")
                    return
            except Exception as e:
                logger.error(f"❌ [DB] Error inesperado en insert: {e}")
                return

        try:
            keys = list(data.keys())
            values = list(data.values())
            placeholders = ", ".join(["?"] * len(keys))
            
            sql = f"INSERT INTO {table} ({', '.join(keys)}) VALUES ({placeholders})"
            
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                conn.execute(sql, values)
                conn.commit()
        except Exception as e:
            logger.error(f"❌ [DB] Error síncrono en insert: {e}")


    async def insert_many(self, table: str, rows: List[Dict[str, Any]]):
        """Inserta múltiples registros de forma eficiente."""
        if not rows:
            return
            
        max_retries = 5
        for i in range(max_retries):
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._insert_many_sync, table, rows)
                return
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() and i < max_retries - 1:
                    wait_time = (i + 1) * 0.5
                    logger.warning(f"⚠️ [DB] Base de datos bloqueada en batch. Reintentando en {wait_time}s... (Intento {i+1})")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"❌ [DB] Error en insert_many: {e}")
                    return
            except Exception as e:
                logger.error(f"❌ [DB] Error inesperado en insert_many: {e}")
                return

    def _insert_many_sync(self, table: str, rows: List[Dict[str, Any]]):
        if not rows:
            return
            
        try:
            keys = list(rows[0].keys())
            placeholders = ", ".join(["?"] * len(keys))
            sql = f"INSERT INTO {table} ({', '.join(keys)}) VALUES ({placeholders})"
            
            values = [tuple(row[k] for k in keys) for row in rows]
            
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                conn.executemany(sql, values)
                conn.commit()
        except Exception as e:
            logger.error(f"❌ [DB] Error síncrono en insert_many: {e}")



    async def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Ejecuta una consulta y retorna una lista de diccionarios."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._query_sync, sql, params)

    def _query_sync(self, sql: str, params: tuple) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

# Singleton
_db_instance = None
def get_db() -> Database:
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
