import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
import base64
from googletrans import Translator
from langdetect import detect
import googleapiclient.discovery

load_dotenv()  # Load environment variables

# Configure API keys
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
youtube_api_key = os.getenv("YOUTUBE_API_KEY")

prompt = """You are a YouTube video summarizer. You will take the transcript text
and summarize the entire video, providing the important points in a concise format. """

translator = Translator()

# Function to detect language of text
def detect_language(text):

    return detect(text)

# Function to translate text to English
def translate_to_english(text, source_lang):
    translated = translator.translate(text, src=source_lang, dest='en')
    return translated.text

# Function to translate summary to target language
def translate_summary(summary, target_lang):
    source=detect_language(summary)
    translated = translator.translate(summary, src=source, dest=target_lang)
    return translated.text

# Function to extract transcript from YouTube video for all available languages
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
        
        # Return concatenated transcript text and video id
        return transcript_text, video_id
    
    except Exception as e:
        st.error(f"Error extracting transcript: {str(e)}")
        return None, None

# Function to generate summary using Gemini Pro
def generate_summary(transcript_text, prompt, summary_percentage):
    
    # Initialize the model
    model = genai.GenerativeModel("gemini-pro")
    
    # Generate the summary
    summary = model.generate_content(prompt+transcript_text)
    target_summary_length = int(len(summary.text) * (summary_percentage / 100))

    full_prompt = (
        f"Here is the text to summarize:\n{summary.text}\n\n"
        f"Please summarize the above text to approximately {target_summary_length} in a concised format."
    )
    response = model.generate_content(full_prompt)

    return response.text


# Function to get video details using YouTube Data API
def get_video_details(video_id):
    try:
        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=youtube_api_key)
        request = youtube.videos().list(part="snippet", id=video_id)
        response = request.execute()

        if response["items"]:
            title = response["items"][0]["snippet"]["title"]
            description = response["items"][0]["snippet"]["description"]
            return title, description
        else:
            return None, None
    except Exception as e:
        st.error(f"Error fetching video details: {str(e)}")
        return None, None

# Custom CSS for styling with animations and Instagram palette colors
def add_custom_css():
    st.markdown(
        """
        <style>
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .title {
            text-align: center;
            font-size: 3em;
            color: white;
            margin-bottom: 20px;
            font-weight: bold;
            background: linear-gradient(45deg, #833ab4, #fd1d1d, #fcb045);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradient 5s ease infinite;
        }
        .video-thumbnail {
            max-width: 100%;
            margin-top: 20px;
            height: auto;
        }
        .summary-title {
            font-size: 1.5em;
            color: black;
        }
        .button-container {
            display: flex;
            justify-content: flex-end;
        }
        .button-container a {
            text-decoration: none;
            color: white;
        }
        .download-button {
            background-color: black;
            color: white;
            font-weight: bold;
            border: none;
            padding: 3px 6px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 12px;
            cursor: pointer;
            border-radius: 3px;
            transition: background-color 0.3s;
        }
        .download-button:hover {
            background-color: green;
        }
        .column-space {
            margin-right: 20px;
        }
        .summary-button {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            cursor: pointer;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        .summary-button:hover {
            background-color: #45a049;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Apply custom CSS
add_custom_css()

# Streamlit app layout
st.markdown('<h1 class="title">YouTube Video Summarizer</h1>', unsafe_allow_html=True)

youtube_link = st.text_input("Enter YouTube Video Link:")
target_language = st.selectbox(
    "Select Target Language for Summary:",
    ["English", "French", "German", "Spanish", "Telugu", "Hindi", "Malayalam", "Tamil", "Kannada"]
)
summary_percentage = st.slider("Select Summary Length (%) :", 1, 100, 50, 1)

if st.button("Get Summary"):
    if youtube_link:
        try:
            transcript_text, video_id = extract_transcript_details(youtube_link)
            if not transcript_text:
                st.warning("No transcription details found for the provided link.")
            else:
                video_title, _ = get_video_details(video_id)
                
                if transcript_text:
                    # Detect the language of the transcript
                    try:
                        source_lang = detect_language(transcript_text)
                    except Exception as e:
                        st.warning(f"Language detection failed: {str(e)}")
                        source_lang = 'en'  # Default to English if detection fails
                    
                    # Generate summary based on the detected language (default to English)
                    summary = generate_summary(transcript_text, prompt, summary_percentage)
                    
                    # Translate summary to the selected target language if not English
                    if target_language != source_lang:
                        try:
                            summary = translate_summary(summary, target_language.lower())
                        except Exception as e:
                            st.warning(f"Translation failed: {str(e)}")
                    
                    col1, col_space, col2 = st.columns([1, 0.1, 1])
                    
                    with col1:
                        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True, caption=video_title)
                    
                    with col2:
                        b64_summary = base64.b64encode(summary.encode()).decode()
                        st.markdown(f'<h2 class="summary-title">Summary for "{video_title}":</h2>', unsafe_allow_html=True)
                        st.markdown(f'<p><strong>Summary Percentage:</strong> {summary_percentage}%</p>', unsafe_allow_html=True)
                        
                    st.markdown(
                            """
                            <div style='background-color: #F8FBFE; padding: 10px; border-radius: 5px; color: black; border: 1px solid black; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); transition: box-shadow 0.3s;'>
                                <div class="button-container">
                                    <a class="download-button" href="data:text/plain;base64,{b64_summary}" download="{video_title}.txt">Download</a>
                                </div>
                                <p>{summary}</p>
                            </div>
                            """.format(b64_summary=b64_summary, video_title=video_title, summary=summary),
                            unsafe_allow_html=True
                    )
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a YouTube video link.")