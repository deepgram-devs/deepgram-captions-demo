import streamlit as st
from streamlit_player import st_player
from helpers import get_caption_at_time, parse_srt, parse_webvtt, is_valid_youtube_url
from captions import transcribe_file

custom_header = """
    <style>
        .custom-header {
            display: flex;
            flex-direction: column;
        }
        .divider {
            flex-grow: 1;
            height: 1px;
            background: linear-gradient(to right, #FF2EEA, #4B3CFF);
            margin-bottom: 1rem;
        }
    </style>
    <div class="custom-header">
        <h1>SRT WebVTT Captions</h1>
        <div class="divider"></div>
    </div>
"""


# STATE

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
        "webvtt_speakers":""
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
        st.session_state.transcription = captions[2]
        st.session_state.captions["webvtt_speakers"] = captions[3]


def run():
    st.set_page_config(
        page_title="SRT WebVTT Captions",
        page_icon="🗣️",
    )

    st.markdown(custom_header, unsafe_allow_html=True)
    st.markdown(
        """This demo uses the open source python package [deepgram-captions](https://github.com/deepgram/deepgram-python-captions) to create webvtt and srt captions from the Deepgram speech-to-text API transcription response. The package can also be used with other speech-to-text transcription formats such as whisper-timestamped. (See the package readme for more info.)""",
        unsafe_allow_html=False,
    )

    caption_choice = st.selectbox("Select your type of captions:", ("srt", "webvtt"))

    url = st.text_input("YouTube URL", "https://www.youtube.com/watch?v=MPmx09S4cLw")
    speakers = st.checkbox("Add speakers (webvtt only)")
    video_options = st.session_state.video_options

    # Get captions in webvtt and srt format
    if st.session_state.transcription == None:
        get_captions(url)

    # Transcribe the audio when the user enters a new URL
    if st.session_state.url != url:
        if is_valid_youtube_url(url):
            st.session_state.url = url
            get_captions(url)
        else:
            st.warning("Please enter a valid YouTube URL in the expected format: `https://www.youtube.com/watch?v=MPmx09S4cLw`")

    event = st_player(url, **video_options, key="youtube_player")

    if st.session_state.youtube_player:
        played_seconds = st.session_state.youtube_player["data"]["playedSeconds"]
        #   Display and use srt captions in the demo:
        if caption_choice == "srt":
            srt_captions_dict = parse_srt(st.session_state.captions["srt"])
            current_caption_srt = get_caption_at_time(srt_captions_dict, played_seconds)
            st.markdown(
                f'<span style="display: block; height: 100px; text-align: center; font-size: 1.7em; color:#FF2EEA; font-weight:600;">{current_caption_srt}</span>',
                unsafe_allow_html=True,
            )
            if st.session_state.youtube_player["data"]["played"] > 0:
                st.subheader("Full srt captions for the entire video:")
                st.code(st.session_state.captions["srt"], language="text")
        #   Display and use webvtt captions (with speakers) in the demo:
        if caption_choice == "webvtt" and speakers:
            webvtt_captions_dict = parse_webvtt(st.session_state.captions["webvtt_speakers"])
            current_caption_webvtt = get_caption_at_time(
                webvtt_captions_dict, played_seconds
            )
            st.markdown(
                f'<span style="display: block; height: 100px; text-align: center; font-size: 1.7em; color:#13EF93; font-weight:600;">{current_caption_webvtt}</span>',
                unsafe_allow_html=True,
            )
            if st.session_state.youtube_player["data"]["played"] > 0:
                st.subheader("Full webvtt captions for the entire video:")
                st.code(st.session_state.captions["webvtt_speakers"], language="text")
        #   Display and use webvtt captions (without speakers) in the demo:
        else:
            webvtt_captions_dict = parse_webvtt(st.session_state.captions["webvtt"])
            current_caption_webvtt = get_caption_at_time(
                webvtt_captions_dict, played_seconds
            )
            st.markdown(
                f'<span style="display: block; height: 100px; text-align: center; font-size: 1.7em; color:#13EF93; font-weight:600;">{current_caption_webvtt}</span>',
                unsafe_allow_html=True,
            )
            if st.session_state.youtube_player["data"]["played"] > 0:
                st.subheader("Full webvtt captions for the entire video:")
                st.code(st.session_state.captions["webvtt"], language="text")


if __name__ == "__main__":
    run()
