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
if 'selections' not in st.session_state:
    st.session_state.selections = {
        "srt": True,
        "webvtt": False,
    }

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

def parse_webvtt(webvtt_text):
    captions = []
    lines = webvtt_text.strip().split("\n")
    
    # Skip the header lines
    lines = lines[4:]
    
    for line in lines:
        time_range = line.split(" --> ")
        if len(time_range) == 2:
            start_time = time_range[0]
            end_time = time_range[1]
            text = lines[lines.index(line) + 1]
            captions.append({
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

    st.header('Deepgram Captions', divider="rainbow")

    # st.write(st.session_state)

    video_options = st.session_state.video_options

    caption_choice = st.selectbox(
    'Select your type of captions:',
    ('srt', 'webvtt'))

    url = st.text_input("First URL", "https://www.youtube.com/watch?v=dg4NAG6HYmE")

    # if st.button("Play/Pause"):
    #     video_options["playing"] = not video_options["playing"]

    event = st_player(url, **video_options, key="youtube_player")
    if st.session_state.youtube_player:
      played_seconds = st.session_state.youtube_player["data"]["playedSeconds"]
      if caption_choice == "srt":
        srt_captions_dict = parse_srt(st.session_state.captions["srt"])
        # st.text(srt_captions_dict)
        current_caption_srt = get_caption_at_time(srt_captions_dict, played_seconds)
        st.markdown(f'<span style="display: block; height: 100px; text-align: center; font-size: 1.3em; color:purple; font-weight:600;">{current_caption_srt}</span>', unsafe_allow_html=True)
        # if st.session_state.youtube_player:
        if st.session_state.youtube_player["data"]["played"] > 0:
          st.text("Full srt captions for the entire video:")
          st.text(st.session_state.captions["srt"])
      if caption_choice == "webvtt":
        webvtt_captions_dict = parse_webvtt(st.session_state.captions["webvtt"])
        # st.write(webvtt_captions_dict)
        current_caption_webvtt = get_caption_at_time(webvtt_captions_dict, played_seconds)
        st.markdown(f'<span style="display: block; height: 100px; text-align: center; font-size: 1.3em; color:blue; font-weight:600;">{current_caption_webvtt}</span>', unsafe_allow_html=True)
        if st.session_state.youtube_player["data"]["played"] > 0:
          st.text("Full webvtt captions for the entire video:")
          st.text(st.session_state.captions["webvtt"])

  # Transcribe the audio when the user enters a new URL
    if st.session_state.url != url:
        st.session_state.url = url
        st.session_state.captions["webvtt"], st.session_state.captions["srt"], st.session_state.transcription = transcribe_file(url)

if __name__ == "__main__":
    run()
