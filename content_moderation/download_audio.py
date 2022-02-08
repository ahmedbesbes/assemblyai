from argparse import ArgumentParser
from pytube import YouTube


def download_audio(video_url):
    try:
        yt = YouTube(video_url)
        audio_streams = yt.streams.filter(only_audio=True)
        audio_stream = audio_streams[0]
        path = audio_stream.download("../data")
        print(f"Video downloaded !")
        print(path)
    except Exception as e:
        print(e)
        print("error with the provided URL")


if __name__ == "__main__":
    argument_parser = ArgumentParser()
    argument_parser.add_argument("--url")
    args = argument_parser.parse_args()

    download_audio(args.url)
