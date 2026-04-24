import asyncio
import os
from prisma import Prisma

async def main():
    p = Prisma()
    await p.connect()
    # Ejecutamos una consulta directa o vemos la URL de conexion
    try:
        print("URL del motor PRISMA:", getattr(p._engine, 'url', 'N/A'))
        print("CWD:", os.getcwd())
        # Imprimir dónde buscó el archivo sqlite
        tables = await p.query_raw("SELECT name FROM sqlite_master WHERE type='table'")
        print("TABLAS ENCONTRADAS POR PRISMA:", tables)
    except Exception as e:
        print("ERROR:", e)
    finally:
        await p.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
