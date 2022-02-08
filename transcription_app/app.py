import os
import requests
import streamlit as st
from pytube import YouTube
import validators

from dotenv import load_dotenv

st.set_page_config(layout="wide")
load_dotenv()


@st.cache(allow_output_mutation=True)
def download_audio(video_url):
    try:
        yt = YouTube(video_url)
        audio_streams = yt.streams.filter(only_audio=True)
        audio_stream = audio_streams[0]
        with st.spinner("Downloading the audio file of the Youtube video"):
            path = audio_stream.download("../data")
        return path
    except Exception as e:
        st.error(
            "Something bad happend when processing the url : here's the error message"
        )
        st.code(f"error: {e}", language="shell")


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


def submit(url):
    endpoint = "https://api.assemblyai.com/v2/transcript"
    json = {"audio_url": url}
    headers = {
        "authorization": os.environ["API_KEY"],
        "content-type": "application/json",
        "auto_chapters": "True",
    }
    response = requests.post(endpoint, json=json, headers=headers)
    json_response = response.json()
    return json_response


def poll(transcription_id):
    endpoint = f"https://api.assemblyai.com/v2/transcript/{transcription_id}"
    headers = {
        "authorization": os.environ["API_KEY"],
    }
    response = requests.get(endpoint, headers=headers)
    json_response = response.json()
    return json_response


video_url = st.text_input("Enter a youtube video URL")

if validators.url(video_url):
    path = download_audio(video_url)
    st.write(f"audio saved to `{path}`")
    filename = path.split("/")[-1]

    bt_upload_file = st.button(
        "Upload file to AssemblyAI",
    )
    if bt_upload_file:
        with st.spinner("Uploading file to AssemblyAI"):
            json_response = upload(path)
            st.write(json_response)

            try:
                upload_url = json_response["upload_url"]
                st.session_state["upload_url"] = upload_url
            except KeyError:
                upload_url = None

    if "upload_url" in st.session_state:
        bt_transcribe = st.button(
            "Transcribe file",
        )

        if bt_transcribe:
            upload_url = st.session_state["upload_url"]
            submission = submit(upload_url)
            st.session_state["id"] = submission["id"]
            st.write(submission)

    if "id" in st.session_state:
        bt_poll = st.button("retrieve result")

        with st.spinner("Retrieving output ..."):
            result = poll(st.session_state["id"])

        text = result["text"]

        columns = st.columns(2)

        with columns[0]:
            with st.expander("Show text"):
                st.write(text)

        with columns[1]:
            with st.expander("Show text"):
                st.write(result)

else:
    st.error("Please enter a valid url")
