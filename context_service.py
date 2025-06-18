import motor.motor_asyncio
from db import get_collection


async def fetch_context() -> list:
    collection = get_collection()
    cursor = collection.find()
    data = []
    async for doc in cursor:

        data.append(doc)
    return data
