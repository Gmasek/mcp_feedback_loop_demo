import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()
URL = os.getenv("MONGODB")


def get_collection():

    client = motor.motor_asyncio.AsyncIOMotorClient(URL)
    db = client["Notification_feedback"]

    return db["Feedbacks"]
