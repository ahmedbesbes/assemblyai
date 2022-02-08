from argparse import ArgumentParser
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def submit(url):
    endpoint = "https://api.assemblyai.com/v2/transcript"
    json = {
        "audio_url": url,
        "content_safety": True,
    }
    headers = {
        "authorization": os.environ["API_KEY"],
        "content-type": "application/json",
    }
    response = requests.post(endpoint, json=json, headers=headers)
    json_response = response.json()
    return json_response


if __name__ == "__main__":
    argument_parser = ArgumentParser()
    argument_parser.add_argument("--url")
    args = argument_parser.parse_args()

    response = submit(args.url)

    print(response)
