from haystack import Pipeline
from haystack.dataclasses import ChatMessage
from haystack.components.generators.chat import OpenAIChatGenerator

from haystack.utils import Secret
from haystack import component
from bson import ObjectId
from pymongo import MongoClient
from typing import List, Optional
from dotenv import load_dotenv
import os


@component
class MongoDataFetcher:

    @component.output_types(messages=list[ChatMessage])
    def run(self, tone: str, res_to_fix: list[ChatMessage] = None):
        self.client = MongoClient(os.getenv("MONGODB"))
        self.collection = self.client["Notification_feedback"]["Feedbacks"]
        documents = self.collection.find()

        data = {"feedbacks": []}

        for doc in documents:
            data["feedbacks"].append(
                {
                    "Motivational_quote": doc["Response"],
                    "rating": doc["rating"],
                    "text_feedback": doc["text_rating"],
                }
            )
        self.data = data

        if res_to_fix == None:

            messages = [
                ChatMessage.from_system(
                    """You are a helpful and motiviating assistant that creates motivational messages. Try to keep them short. Suggest some low intesity activity for them to do in {tone} tone
                    Only respond with the Quote not a title, respond in one line no line breaks
                    
                    """
                ),
                ChatMessage.from_user(
                    f"Create a notification for this person this is the ratings for previous ratings {self.data}"
                ),
            ]
            return {"messages": messages}

        if res_to_fix != None:
            print(res_to_fix[0].text)
            messages = [
                ChatMessage.from_system(
                    "You are a message shortener tool, shorten messages that are being sent to you to less then 120 chars "
                ),
                ChatMessage.from_user(
                    f"Fix this notification this is too long {res_to_fix[0].text} max 120 chars including whitespace"
                ),
            ]
            return {"messages": messages}


@component
class OutputValidator:
    def __init__(self):
        pass

    @component.output_types(
        valid_reply=List[ChatMessage],
        invalid_replies=List[ChatMessage],
        error_message=Optional[str],
    )
    def run(self, reply: List[ChatMessage]):
        try:
            motivation = reply[0].text

            if validate(motivation):
                print("Response valid returning ")
                return {"valid_replies": reply}
            else:
                print("INVALIDINVALIDinvalid?")

                return {"invalid_replies": reply}
        except ValueError as e:

            return {"invalid_replies": reply}


def validate(msg: str) -> bool:

    letter_count = len(msg)
    whitespaceCount = 0
    for i in range(len(msg) - 1):
        if msg[i].isspace():
            whitespaceCount += 1

    if whitespaceCount > 20:

        return False
    elif whitespaceCount < 20 and letter_count < 130:

        return True
    else:

        return False


from haystack_integrations.components.generators.ollama import OllamaChatGenerator

# Initialize the generator
generator = OllamaChatGenerator(
    model="mistral:7b",
)

# Create the pipeline
pipeline = Pipeline(max_runs_per_component=5)
pipeline.add_component("validator", OutputValidator())
# Add both components
pipeline.add_component("fetcher", MongoDataFetcher())
pipeline.add_component("generator", generator)

# Connect them
pipeline.connect("fetcher", "generator")
pipeline.connect("generator.replies", "validator")
pipeline.connect("validator.invalid_replies", "fetcher.res_to_fix")

print()
