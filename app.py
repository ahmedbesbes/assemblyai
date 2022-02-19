import re
import streamlit as st
from streamlit_player import st_player
from youtube_transcriber import YoutubeTranscriber

st.set_page_config(layout="wide")


def clean_video_url(video_url):
    video_url = re.sub(f"&.*", "", video_url)
    return video_url


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

    return youtube_transcriber.transcription


video_url = st.sidebar.text_input("Enter youtube video")
video_url = clean_video_url(video_url)


columns = st.columns((1, 2, 1))
with columns[1]:
    st_player(video_url, height=500)


if video_url.strip() != "":
    use_content_moderation = st.sidebar.checkbox("Use content moderation", value=False)
    use_topic_detection = st.sidebar.checkbox("Use topic detection", value=False)

    transcribe_button = st.sidebar.button("Transcribe audio")

    if transcribe_button:

        transcript = transcribe_video(
            video_url,
            use_content_moderation,
            use_topic_detection,
        )

        st.write(transcript)
