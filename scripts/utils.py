import re
import streamlit as st
from streamlit_player import st_player
from scripts.youtube_transcriber import YoutubeTranscriber


examples = {
    "Annie Hall - Opening monologue": {
        "video_url": "https://www.youtube.com/watch?v=5h5zurZsIQY",
        "name": "Annie Hall (112) Movie CLIP - Opening Monologue (1977) HD",
    },
    "Elon Musk Might be A Supper Villain": {
        "video_url": "https://www.youtube.com/watch?v=gV6hP9wpMW8",
        "name": "Annie Hall (112) Movie CLIP - Opening Monologue (1977) HD",
    },
    "Machine Learning in 5 Minutes": {
        "video_url": "https://www.youtube.com/watch?v=-DEL6SVRPw0",
        "name": "Machine Learning In 5 Minutes  Machine Learning Introduction What Is Machine Learning Simplilearn",
    },
    "Martin Luther King Jr I have A Dream": {
        "video_url": "https://www.youtube.com/watch?v=3vDWWy4CMhE",
        "name": "Martin Luther King Jr I Have A Dream Speech",
    },
    "WHO's Science in 5 FLu & COVID-19": {
        "video_url": "https://www.youtube.com/watch?v=ceBgCLG-QbY",
        "name": "WHO’s Science in 5 Flu & COVID-19",
    },
}


def clean_video_url(video_url):
    video_url = re.sub(f"&.*", "", video_url)
    return video_url


def show_youtube_thumbnail(video_url):
    columns = st.columns((1, 2, 1))
    with columns[1]:
        st_player(
            video_url,
            height=500,
        )


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def transcribe_video(
    video_url,
    use_content_moderation,
    use_topic_detection,
):
    youtube_transcriber = YoutubeTranscriber(
        video_url,
        content_safety=use_content_moderation,
        iab_categories=use_topic_detection,
    )

    with st.spinner("Downloading audio"):
        if youtube_transcriber.downloaded_audio_path is None:
            youtube_transcriber.download_audio()
            st.success(
                f"Audio downloaded to {youtube_transcriber.downloaded_audio_path}"
            )
        else:
            st.info("hello")

    with st.spinner("Uploading audio"):
        if youtube_transcriber.upload_url is None:
            youtube_transcriber.upload_audio()
            st.success(f"upload url: {youtube_transcriber.upload_url}")

    with st.spinner("Submitting a job for processing queue"):
        if youtube_transcriber.transcription_id is None:
            youtube_transcriber.submit()
            st.info(
                f"A transcription job (id={youtube_transcriber.transcription_id}) has been submitted"
            )

    with st.spinner("Polling the result"):
        if youtube_transcriber.transcription is None:
            youtube_transcriber.poll()
            st.success("Transcription succeeded")

    output_name = youtube_transcriber.downloaded_audio_path.split("/")[-1].rstrip(
        ".mp4"
    )
    output_name = output_name.replace(" ", "_")

    youtube_transcriber.save_transcript(output_name)

    return youtube_transcriber.transcription


def visualize_result(video_url, result):
    text = result["text"]
    labels = result["labels"]
    timestamp = result["timestamp"]
    start = timestamp["start"]
    end = timestamp["end"]

    st.info(f"⏱️ Start time : **{start}** | End time: **{end}**")

    st_player(
        video_url,
        config={"playerVars": {"start": int(start / 1000), "end": int(end / 1000) + 1}},
    )

    st.markdown(f"**text**: {text}")

    expander = st.expander("Visualize topics")

    with expander:
        for label in labels:
            relevance = label["relevance"]
            label = label["label"]
            st.markdown(f"- `{label}` : {relevance:.4f}")


def show_output(video_url, transcript, use_topic_detection):
    show_youtube_thumbnail(video_url)

    cols = st.columns(2)

    with cols[0]:
        st.header("Transcription output")
        st.write(transcript)

    if use_topic_detection:
        with cols[1]:
            st.header("Topic extraction by video segment")
            results = transcript["iab_categories_result"]["results"]
            for result in results:
                visualize_result(video_url, result)
