import streamlit as st
import asyncio
from deepgram import Deepgram
from deepgram_captions import DeepgramConverter, webvtt, srt
from pytube import YouTube
from helpers import clean_filename

def get_diarized(audio_file_path):
    api_key = st.secrets["DEEPGRAM_API_KEY"]
    deepgram = Deepgram(api_key)
    audio = open(audio_file_path, "rb")

    source = {"buffer": audio, "mimetype": "audio/mpeg"}
    response = asyncio.run(
        deepgram.transcription.prerecorded(
            source,
            {
                "smart_format": True,
                "model": "nova",
                "diarize": True
            },
        )
    )
    return response


# Define a cache for the audio file download and transcription
@st.cache_data
def transcribe_file(url):
    
    yt = YouTube(url)
    cleaned_title = clean_filename(yt.title)

    # Download the audio stream
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_file_path = f"./audio_files/{cleaned_title}.mp3"
    audio_stream.download(output_path="audio_files", filename=cleaned_title + ".mp3")

    # Transcribe the audio file
    api_key = st.secrets["DEEPGRAM_API_KEY"]
    deepgram = Deepgram(api_key)
    audio = open(audio_file_path, "rb")
    source = {"buffer": audio, "mimetype": "audio/mpeg"}
    diarized = get_diarized(audio_file_path)
    response = asyncio.run(
        deepgram.transcription.prerecorded(
            source,
            {
                "smart_format": True,
                "model": "nova",
            },
        )
    )

    # Extract captions from the response
    transcription = DeepgramConverter(response)
    transcription_with_speakers = DeepgramConverter(diarized)
    web_vtt = webvtt(transcription)
    web_vtt_speakers = webvtt(transcription_with_speakers)
    srt_captions = srt(transcription)

    return web_vtt, srt_captions, response, web_vtt_speakers
