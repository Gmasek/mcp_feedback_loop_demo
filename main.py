from context_service import fetch_context
import asyncio
from client import query_ollama
from db import get_collection
from pipeline import pipeline


### Obv get this from user when integrated
def get_valid_rating() -> int:
    while True:
        rating_input = input("Rate the response (1-5): ").strip()

        if not rating_input:
            print("Rating cannot be empty. Please enter a number between 1 and 5.")
            continue

        if not rating_input.isdigit():
            print("Rating must be a number. Try again.")
            continue

        rating = int(rating_input)
        if 1 <= rating <= 5:
            return rating
        else:
            print("Rating must be between 1 and 5.")


def get_text_input():
    text_rating = input("How would you change the response? ").strip()
    return text_rating


#### NON PIPELINE RUN
# async def main():
#    context = await fetch_context()
#
#    prompt = f"""
#    {context} these are the past notifiactions generated 1 means terrible 5 means good \n\n
#    User: Create a motivational message for me keep the response decently short
#     --IMPORTANT--  dont reuse any of the previous messages
#   maximum 30 words 1 quote
#    \nAssistant:"""
#
#    response = await query_ollama(prompt)
#
#    print(f" {response.strip()}\n")
#
#    # Get rating
#    rating = rating = get_valid_rating()
#    ratings = get_collection()
#    await ratings.insert_one({"Response": response, "rating": rating})
#
#    print("Saved to MongoDB!")


#### Pipeline main function
async def main():
    response = pipeline.run({"fetcher": {"tone": "Cheerful"}})
    res_text = response["validator"]["valid_replies"][-1].text
    print(f" {res_text.strip()}\n")
    # Get rating
    rating = get_valid_rating()
    ratings = get_collection()
    text_rating = get_text_input()
    await ratings.insert_one(
        {"Response": res_text, "rating": rating, "text_rating": text_rating}
    )
    print("Saved to MongoDB!")


if __name__ == "__main__":
    while True:
        asyncio.run(main())
