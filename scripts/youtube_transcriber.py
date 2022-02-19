import os
import sys
import time
import json
import requests
from pytube import YouTube


def read_file(filename, chunk_size=5242880):
    with open(filename, "rb") as _file:
        while True:
            data = _file.read(chunk_size)
            if not data:
                break
            yield data


class YoutubeTranscriber(object):
    def __init__(self, api_key, video_url, content_safety=False, iab_categories=False):

        self.api_key = api_key
        self.video_url = video_url
        self.content_safety = content_safety
        self.iab_categories = iab_categories
        self.downloaded_audio_path = None
        self.upload_url = None
        self.transcription_id = None
        self.transcription = None

    def download_audio(self):
        try:
            yt = YouTube(self.video_url)
            audio_streams = yt.streams.filter(only_audio=True)
            audio_stream = audio_streams[0]
            path = audio_stream.download("./data/audio")
            self.downloaded_audio_path = path
            print(f"audio successuffly downloaded to : {path}")
        except Exception as e:
            print(e)
            print("error with the provided URL")

    def upload_audio(self):
        if self.downloaded_audio_path is not None:
            headers = {"authorization": self.api_key}
            response = requests.post(
                "https://api.assemblyai.com/v2/upload",
                headers=headers,
                data=read_file(self.downloaded_audio_path),
            )
            json_response = response.json()
            upload_url = json_response["upload_url"]
            self.upload_url = upload_url
            print(f"upload_url : {upload_url}")
            return upload_url
        else:
            raise ValueError("no audio file provided")

    def submit(self):
        if self.upload_url is not None:
            endpoint = "https://api.assemblyai.com/v2/transcript"
            json = {
                "audio_url": self.upload_url,
                "content_safety": self.content_safety,
                "iab_categories": self.iab_categories,
            }
            headers = {
                "authorization": self.api_key,
                "content-type": "application/json",
            }
            response = requests.post(endpoint, json=json, headers=headers)
            json_response = response.json()

            transcription_id = json_response["id"]
            self.transcription_id = transcription_id
            print(
                f"A transcription job (id={self.transcription_id}) has been submitted"
            )

        else:
            raise ValueError(
                "upload_url has not been set yet. Please upload an audio file"
            )

    def poll(self):
        if self.transcription_id is not None:
            endpoint = (
                f"https://api.assemblyai.com/v2/transcript/{self.transcription_id}"
            )
            headers = {
                "authorization": self.api_key,
            }
            status = ""
            print("polling data ...")
            while status != "completed":
                response = requests.get(endpoint, headers=headers).json()
                status = response["status"]
                if status == "error":
                    sys.exit("Audio failed to process.")
                elif status != "completed":
                    print("sleeping 5s")
                    time.sleep(5)

            print("transcription succeeded and avaialbe in the transcription attribute")
            self.transcription = response
        else:
            raise ValueError("no transcription id provided")

    def save_transcript(self, output_name):
        output_path = os.path.join(
            "./transcripts/",
            f"{output_name}.json",
        )
        with open(output_path, "w") as f:
            json.dump(self.transcription, f)
