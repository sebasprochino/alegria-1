import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

from src.services.nexus import service as nexus_service
from src.services.database import service as db_service

async def test_history():
    print("🚀 Starting History Verification...")
    
    # 1. Initialize DB
    await db_service.connect()
    
    # 2. Create Session
    session_id = await nexus_service.create_session()
    print(f"✅ Session Created: {session_id}")
    
    # 3. Save User Message
    await nexus_service.save_message(session_id, "user", "Hello Anima!")
    print("✅ User Message Saved")
    
    # 4. Save Anima Message
    await nexus_service.save_message(session_id, "anima", "Hello User!")
    print("✅ Anima Message Saved")
    
    # 5. Retrieve History
    history = await nexus_service.get_conversation_history(session_id)
    print(f"✅ History Retrieved: {len(history)} messages")
    for msg in history:
        print(f"  - {msg['role']}: {msg['content']}")
        
    # 6. Verify Content
    assert len(history) == 2
    assert history[0]['content'] == "Hello Anima!"
    assert history[1]['content'] == "Hello User!"
    
    print("🎉 Verification Successful!")
    await db_service.disconnect()

if __name__ == "__main__":
    asyncio.run(test_history())
