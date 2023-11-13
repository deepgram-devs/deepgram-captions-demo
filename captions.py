import streamlit as st
import os
import asyncio
from dotenv import load_dotenv
from deepgram import Deepgram
from deepgram_captions import DeepgramConverter, webvtt, srt
from pytube import YouTube
from helpers import clean_filename

load_dotenv()


# Define a cache for the audio file download and transcription
@st.cache_data
def transcribe_file(url):
    api_key = os.getenv("DEEPGRAM_API_KEY")
    yt = YouTube(url)
    cleaned_title = clean_filename(yt.title)

    # Download the audio stream
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_file_path = f"./audio_files/{cleaned_title}.mp3"
    audio_stream.download(output_path="audio_files", filename=cleaned_title + ".mp3")

    # Transcribe the audio file
    deepgram = Deepgram(api_key)
    audio = open(audio_file_path, "rb")

    source = {"buffer": audio, "mimetype": "audio/mpeg"}
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
    web_vtt = webvtt(transcription)
    srt_captions = srt(transcription)

    return web_vtt, srt_captions, response
