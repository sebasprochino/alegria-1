import asyncio
from prisma import Prisma

async def get_prefs():
    p = Prisma()
    await p.connect()
    # check default user
    prefs = await p.userpreferences.find_first()
    if prefs:
        print(repr(prefs))
        print("Model fields:", prefs.model_fields.keys())
    else:
        print("No userpreferences found")
    await p.disconnect()

asyncio.run(get_prefs())
