import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from google.generativeai import GenerativeModel
from langdetect import detect
from googletrans import Translator, LANGUAGES

# Initialize Google Translator
translator = Translator()

# Function to detect language of text
def detect_language(text):
    try:
        return detect(text)
    except Exception as e:
        st.warning(f"Language detection failed: {str(e)}")
        return 'en'  # Default to English if detection fails

# Function to translate summary to target language
def translate_summary(summary, target_lang):
    source_lang = detect_language(summary)
    
    if source_lang in LANGUAGES and target_lang.lower() in LANGUAGES:
        try:
            translated = translator.translate(summary, src=source_lang, dest=target_lang.lower())
            return translated.text
        except Exception as e:
            st.warning(f"Translation failed: {str(e)}")
            return summary
    else:
        st.warning("Invalid language code detected. Translation could not be performed.")
        return summary

# Function to extract transcript from YouTube video
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("v=")[1]
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Initialize an empty string to store concatenated transcript text
        transcript_text = ""

        # Iterate over available transcripts (languages)
        for transcript in transcript_list:
            try:
                # Fetch transcript for each language
                segments = transcript.fetch()
                # Concatenate text from each segment
                transcript_text += " ".join([segment['text'] for segment in segments])
            except NoTranscriptFound:
                continue
        
        # Return concatenated transcript text
        return transcript_text
    
    except Exception as e:
        st.error(f"Error extracting transcript: {str(e)}")
        return None

# Function to generate summary using Gemini Pro
def generate_summary(transcript_text):
    # Initialize the model (dummy implementation)
    model = GenerativeModel("gemini-pro")
    full_prompt = (
        f"Here is the text to summarize:\n{transcript_text}\n\n\n\n"
        f"Please summarize the above text to approximately  in a concise format."
    )
    response = model.generate_content(full_prompt)

    return response.text

# Function to handle feedback submission
def submit_feedback(video_id, feedback_text):
    # Placeholder function for feedback submission (dummy implementation)
    st.success(f"Feedback submitted for video ID '{video_id}': {feedback_text}")
    
    # Response to feedback
    st.info("Thank you for your feedback!")

# Streamlit app layout
st.title("YouTube Video Summarizer with Translation and Feedback")

youtube_link = st.text_input("Enter YouTube Video Link:")

target_language = st.selectbox(
    "Select Target Language for Summary:",
    ["English", "telugu", "hindi", "tamil"]
)

if st.button("Get Summary"):
    if youtube_link:
        try:
            transcript_text = extract_transcript_details(youtube_link)
            if not transcript_text:
                st.warning("No transcription details found for the provided link.")
            else:
                # Generate summary based on the extracted transcript
                summary = generate_summary(transcript_text)
                
                st.subheader("Summary:")
                st.write(summary)
                
                # Translate summary if target language is selected
                if target_language != "English":
                    translated_summary = translate_summary(summary, target_language.lower())
                    st.subheader(f"Translated Summary ({target_language}):")
                    st.write(translated_summary)
                
                # Feedback section
                st.subheader("Feedback:")
                feedback_text = st.text_area("Provide your feedback on the summary:")
                if st.button("Submit Feedback"):
                    if youtube_link:
                        video_id = youtube_link.split("v=")[1]
                        submit_feedback(video_id, feedback_text)
                    else:
                        st.warning("No video link provided. Feedback cannot be submitted.")
                    
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a YouTube video link.")
