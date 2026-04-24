import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from src.services.anima import service as anima_service
from src.services.database import service as db_service
from src.services.nexus import service as nexus_service
from src.services.radar import service as radar_service

async def verify_all():
    print("🚀 Starting Full Verification...")
    
    # 1. Initialize DB
    await db_service.connect()
    await anima_service.initialize()
    
    # 2. Test Hydration & Proactive Context
    session_id = "test-session-" + os.urandom(4).hex()
    print(f"✅ Session Created: {session_id}")
    
    # Save a "pending" message
    await nexus_service.save_message(session_id, "user", "Recuérdame investigar sobre la arquitectura de ALEGR-IA mañana.")
    await nexus_service.save_message(session_id, "anima", "Entendido, lo recordaré.")
    
    # Simulate new turn (hydration will trigger)
    print("💧 Testing Hydration and Proactive Greeting...")
    response = await anima_service.respond("Hola de nuevo", session_id=session_id)
    print(f"Anima Response: {response['content'][:100]}...")
    
    # 3. Test Web Reading
    print("🌐 Testing Web Reading...")
    response = await anima_service.respond("Lee esta página y dime de qué trata: https://en.wikipedia.org/wiki/Artificial_intelligence", session_id=session_id)
    print(f"Anima Response (Web Read): {response['content'][:100]}...")
    
    # 4. Test Deep Search
    print("🧠 Testing Deep Search...")
    response = await anima_service.respond("Haz un análisis detallado sobre el futuro de la IA", session_id=session_id)
    print(f"Anima Response (Deep Search): {response['content'][:100]}...")
    
    # 5. Test Dynamic Discovery
    print("📡 Testing Dynamic Model Discovery...")
    discovery = await radar_service.discover_new_assets()
    print(f"Discovery Findings: {len(discovery['findings'])} items found.")
    
    print("🎉 Verification Complete!")
    await db_service.disconnect()

if __name__ == "__main__":
    asyncio.run(verify_all())
