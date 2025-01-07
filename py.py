import streamlit as st
import whisper
from pytube import YouTube

# Download YouTube video
def download_video(url, filename='video.mp4'):
    yt = YouTube(url)
    stream = yt.streams.filter(only_audio=True).first()
    stream.download(filename=filename)
    return filename

# Transcribe video using Whisper
def transcribe_video(filename):
    model = whisper.load_model("base")
    result = model.transcribe(filename)
    return result["text"]

# Streamlit app
st.title('YouTube Video Transcription')
video_url = st.text_input('Enter YouTube video URL')

if st.button('Transcribe'):
    with st.spinner('Downloading and transcribing video...'):
        video_file = download_video(video_url)
        transcription = transcribe_video(video_file)
    st.write("Transcript:")
    st.write(transcription)
