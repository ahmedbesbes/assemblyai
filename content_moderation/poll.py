# o6mg6qtska-418d-4434-a776-c77ac30f6093
from pprint import pprint
import json
from argparse import ArgumentParser
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def poll(transcription_id):
    endpoint = f"https://api.assemblyai.com/v2/transcript/{transcription_id}"
    headers = {
        "authorization": os.environ["API_KEY"],
    }
    response = requests.get(endpoint, headers=headers)
    json_response = response.json()
    return json_response


if __name__ == "__main__":
    argument_parser = ArgumentParser()
    argument_parser.add_argument("--id")
    argument_parser.add_argument("--name")
    args = argument_parser.parse_args()

    response = poll(args.id)

    with open(f"../transcripts/{args.name}.json", "w") as f:
        json.dump(response, f)

    pprint(response)
