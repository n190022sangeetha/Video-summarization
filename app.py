import os
import streamlit as st
from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr
from concurrent.futures import ThreadPoolExecutor
import yt_dlp as youtube_dl
from moviepy.editor import VideoFileClip
from transformers import BartTokenizer, BartForConditionalGeneration

# Function to load audio file
def load_audio(file_path):
    return AudioSegment.from_wav(file_path)


# Function to remove silence
def remove_silence(audio_segment, silence_thresh=-40, min_silence_len=500):
    chunks = split_on_silence(audio_segment, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    return chunks

# Function to combine chunks into one audio segment
def combine_audio_chunks(chunks):
    combined = AudioSegment.empty()
    for chunk in chunks:
        combined += chunk
    return combined

# Function to recognize speech in the audio file
def transcribe_audio(path):
    r = sr.Recognizer()
    with sr.AudioFile(path) as source:
        audio_listened = r.record(source)
        try:
            text = r.recognize_google(audio_listened)
            return text.capitalize()
        except sr.UnknownValueError:
            return ""

# Function that splits the audio file into chunks on silence and applies speech recognition
def get_large_audio_transcription_on_silence(path):
    sound = AudioSegment.from_file(path)
    chunks = split_on_silence(sound, min_silence_len=500, silence_thresh=sound.dBFS - 14, keep_silence=500)
    folder_name = "audio_chunks"
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    
    whole_text = ""
    
    def process_chunk(i, audio_chunk):
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        text = transcribe_audio(chunk_filename)
        os.remove(chunk_filename)  # Clean up chunk file after processing
        return text
    
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda idx_chunk: process_chunk(*idx_chunk), enumerate(chunks, start=1)))
        whole_text = " ".join(filter(None, results))  # Join non-empty strings

    # Clean up chunk directory
    for file in os.listdir(folder_name):
        os.remove(os.path.join(folder_name, file))
    os.rmdir(folder_name)
    
    return whole_text

# Function to download a YouTube video and extract audio
def download_and_extract_audio(video_url, audio_filename):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloaded_video.mp4'
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
        
    video_clip = VideoFileClip('downloaded_video.mp4')
    audio = video_clip.audio
    audio.write_audiofile(audio_filename, codec='pcm_s16le')
    audio.close()
    video_clip.close()
    os.remove('downloaded_video.mp4')

# Function to extract audio from a video file
def extract_audio_from_video(video_file, audio_filename):
    video_clip = VideoFileClip(video_file)
    audio = video_clip.audio
    audio.write_audiofile(audio_filename, codec='pcm_s16le')
    audio.close()
    video_clip.close()

# Function to summarize text using DistilBART
def summarize_with_distilbart(text, max_length=150, min_length=50):
    tokenizer = BartTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")
    model = BartForConditionalGeneration.from_pretrained("sshleifer/distilbart-cnn-12-6")
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs, max_length=max_length, min_length=min_length, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# Main Streamlit app
st.title("Video to Summary")

input_type = st.radio("Choose input type:", ('YouTube URL', 'Local video file'))

audio_filename = 'extracted_audio.wav'

if input_type == 'YouTube URL':
    video_url = st.text_input("Enter the YouTube video URL:")
    if st.button("Process YouTube Video"):
        if video_url:
            with st.spinner("Downloading and processing video..."):
                download_and_extract_audio(video_url, audio_filename)
                transcription = get_large_audio_transcription_on_silence(audio_filename)
                if transcription:
                    st.subheader("Full Transcription")
                    st.text_area("Transcription", transcription, height=200)
                    summarized_text = summarize_with_distilbart(transcription)
                    st.subheader("Summarized Text")
                    st.text_area("Summary", summarized_text, height=100)
                else:
                    st.error("Failed to fetch transcript or transcript is empty.")
                os.remove(audio_filename)
        else:
            st.error("Please enter a valid YouTube URL.")
elif input_type == 'Local video file':
    uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "avi", "mov", "mkv"])
    if uploaded_file is not None:
        with st.spinner("Processing video..."):
            video_file_path = os.path.join("temp_video." + uploaded_file.name.split('.')[-1])
            with open(video_file_path, "wb") as f:
                f.write(uploaded_file.read())
            extract_audio_from_video(video_file_path, audio_filename)
            transcription = get_large_audio_transcription_on_silence(audio_filename)
            if transcription:
                st.subheader("Full Transcription")
                st.text_area("Transcription", transcription, height=200)
                summarized_text = summarize_with_distilbart(transcription)
                st.subheader("Summarized Text")
                st.text_area("Summary", summarized_text, height=100)
            else:
                st.error("Failed to fetch transcript or transcript is empty.")
            os.remove(audio_filename)
            os.remove(video_file_path)