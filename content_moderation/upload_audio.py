from argparse import ArgumentParser
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def read_file(filename, chunk_size=5242880):
    with open(filename, "rb") as _file:
        while True:
            data = _file.read(chunk_size)
            if not data:
                break
            yield data


def upload(path):
    headers = {"authorization": os.environ["API_KEY"]}
    response = requests.post(
        "https://api.assemblyai.com/v2/upload",
        headers=headers,
        data=read_file(path),
    )
    json_response = response.json()
    return json_response


if __name__ == "__main__":
    argument_parser = ArgumentParser()
    argument_parser.add_argument("--audio")
    args = argument_parser.parse_args()

    response = upload(args.audio)
    print(response)
