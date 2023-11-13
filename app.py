import streamlit as st
from streamlit_player import st_player
from helpers import get_caption_at_time, parse_srt, parse_webvtt
from captions import transcribe_file


# STATE
if "selections" not in st.session_state:
    st.session_state.selections = {
        "srt": True,
        "webvtt": False,
    }

if "video_options" not in st.session_state:
    st.session_state.video_options = {
        "events": ["onProgress"],
        "progress_interval": 1000,
        "volume": 1.0,
        "playing": False,
        "loop": False,
        "controls": True,
        "muted": False,
    }

if "captions" not in st.session_state:
    st.session_state.captions = {
        "webvtt": "",
        "srt": "",
    }

if "url" not in st.session_state:
    st.session_state.url = None

if "transcription" not in st.session_state:
    st.session_state.transcription = None


def get_captions(url):
    captions = transcribe_file(url)
    if captions:
        st.session_state.captions["webvtt"] = captions[0]
        st.session_state.captions["srt"] = captions[1]
        st.session_state.transcription = captions


def run():
    st.set_page_config(
        page_title="Deepgram Captions",
        page_icon="👋",
    )

    st.header("Deepgram Captions", divider="rainbow")

    # st.write(st.session_state)

    caption_choice = st.selectbox("Select your type of captions:", ("srt", "webvtt"))

    url = st.text_input("First URL", "https://www.youtube.com/watch?v=kibx5BR6trA")

    video_options = st.session_state.video_options

    # Get captions in webvtt and srt format
    if st.session_state.transcription == None:
        get_captions(url)

    # Transcribe the audio when the user enters a new URL
    if st.session_state.url != url:
        st.session_state.url = url
        get_captions(url)

    event = st_player(url, **video_options, key="youtube_player")

    if st.session_state.youtube_player:
        played_seconds = st.session_state.youtube_player["data"]["playedSeconds"]
        #   Display and use srt captions in the demo:
        if caption_choice == "srt":
            srt_captions_dict = parse_srt(st.session_state.captions["srt"])
            current_caption_srt = get_caption_at_time(srt_captions_dict, played_seconds)
            st.markdown(
                f'<span style="display: block; height: 100px; text-align: center; font-size: 1.3em; color:purple; font-weight:600;">{current_caption_srt}</span>',
                unsafe_allow_html=True,
            )
            if st.session_state.youtube_player["data"]["played"] > 0:
                st.text("Full srt captions for the entire video:")
                st.text(st.session_state.captions["srt"])
        #   Display and use webvtt captions in the demo:
        if caption_choice == "webvtt":
            webvtt_captions_dict = parse_webvtt(st.session_state.captions["webvtt"])
            # st.write(webvtt_captions_dict)
            current_caption_webvtt = get_caption_at_time(
                webvtt_captions_dict, played_seconds
            )
            st.markdown(
                f'<span style="display: block; height: 100px; text-align: center; font-size: 1.3em; color:blue; font-weight:600;">{current_caption_webvtt}</span>',
                unsafe_allow_html=True,
            )
            if st.session_state.youtube_player["data"]["played"] > 0:
                st.text("Full webvtt captions for the entire video:")
                st.text(st.session_state.captions["webvtt"])


if __name__ == "__main__":
    run()
