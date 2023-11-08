import streamlit as st
from pytube import YouTube
from configure import auth_key
import asyncio
from streamlit_player import st_player, _SUPPORTED_EVENTS
from deepgram import Deepgram
from deepgram_captions.converters import DeepgramConverter
from deepgram_captions.webvtt import webvtt
from deepgram_captions.srt import srt



# STATE
if 'video_options' not in st.session_state:
    st.session_state.video_options = {
        "events": ["onProgress"],
        "progress_interval": 1000,
        "volume": 1.0,
        "playing": False,
        "loop": False,
        "controls": True,
        "muted": False,
    }

if 'captions' not in st.session_state:
    st.session_state.captions = {
        "webvtt": "",
        "srt": "",
        # "transcription": {}
    }

if 'url' not in st.session_state:
    st.session_state.url = None

if 'transcription' not in st.session_state:
    st.session_state.transcription = {}

# Define a cache for the audio file download and transcription
@st.cache_data
def transcribe_file(url):
    DEEPGRAM_API_KEY = auth_key
    yt = YouTube(url)
    
    # Download the audio stream
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_file_path = f'./audio_files/{yt.title}.mp3'
    audio_stream.download(output_path='audio_files', filename=yt.title+'.mp3')

    # Transcribe the audio file
    deepgram = Deepgram(DEEPGRAM_API_KEY)
    audio = open(audio_file_path, 'rb')
    source = {
        'buffer': audio,
        'mimetype': 'audio/mpeg'
    }
    response = asyncio.run(
        deepgram.transcription.prerecorded(
            source,
            {
                'smart_format': True,
                'model': 'nova',
            }
        )
    )

    # Extract captions from the response
    transcription = DeepgramConverter(response)
    web_vtt = webvtt(transcription)
    srt_captions = srt(transcription)

    return web_vtt, srt_captions, response

def time_to_seconds(time_str):
    hours, minutes, seconds = map(float, time_str.replace(',', '.').split(':'))
    return hours * 3600 + minutes * 60 + seconds

def get_caption_at_time(captions, played_seconds):
    for caption in captions:
        start_time, end_time = caption["start"], caption["end"]
        start_seconds, end_seconds = time_to_seconds(start_time), time_to_seconds(end_time)
        if start_seconds <= played_seconds <= end_seconds:
            return caption["text"]
    return ""

def parse_srt(srt_text):
    captions = []
    lines = srt_text.strip().split("\n\n")
    for line in lines:
        parts = line.split("\n")
        if len(parts) >= 3:
            index = parts[0]
            time_range = parts[1].split(" --> ")
            if len(time_range) == 2:
                start_time = time_range[0]
                end_time = time_range[1]
                text = "\n".join(parts[2:])
                captions.append({
                    "index": index,
                    "start": start_time,
                    "end": end_time,
                    "text": text,
                })
    return captions

def run():
    st.set_page_config(
        page_title="Deepgram Captions",
        page_icon="👋",
        # layout="wide",
    )

    # st.write(st.session_state)

    video_options = st.session_state.video_options

    url = st.text_input("First URL", "https://www.youtube.com/watch?v=dg4NAG6HYmE")

    # if st.button("Play/Pause"):
    #     video_options["playing"] = not video_options["playing"]

    event = st_player(url, **video_options, key="youtube_player")
    if st.session_state.youtube_player:
      played_seconds = st.session_state.youtube_player["data"]["playedSeconds"]
    if st.session_state.captions["srt"]:
      # st.text("Test")
      srt_captions_dict = parse_srt(st.session_state.captions["srt"])
      st.text(srt_captions_dict)
      current_caption_srt = get_caption_at_time(srt_captions_dict, played_seconds)
      st.text(current_caption_srt)

    # Transcribe the audio when the user enters a new URL
    if st.session_state.url != url:
        st.session_state.url = url
        st.session_state.captions["webvtt"], st.session_state.captions["srt"], st.session_state.transcription = transcribe_file(url)

    if st.session_state.transcription:
      st.json(st.session_state.transcription, expanded=False)


    col1, col2 = st.columns(2)

    display_webvtt = None
    display_srt = None
    if st.session_state.captions["webvtt"]:
        with col1:
            display_webvtt = st.checkbox("Display webVTT Captions")
    if display_webvtt and st.session_state.captions["webvtt"]:
        with col1:
            st.text(st.session_state.captions["webvtt"])

    # Display SRT captions using a checkbox
    if st.session_state.captions["srt"]:
        with col2:
            display_srt = st.checkbox("Display SRT Captions")
    
    if display_srt and st.session_state.captions["srt"]:
        with col2:
            st.text(st.session_state.captions["srt"])

if __name__ == "__main__":
    run()
