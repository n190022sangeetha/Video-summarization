# Video-summarization


Youtube video summarization involves building a streamlit application designed to provide efficient summarization based on their transcripts using natural language processing and Gemini AI Generative model.

The YouTube Video Summarizer is a Streamlit-based web application that extracts, summarizes, and translates transcripts of YouTube videos. It leverages YouTube Transcript API, Google Generative AI, and Google Translator to provide concise and multi-language summaries for educational and informational videos.



Features :

1)Transcript Extraction:
Extracts transcript text from YouTube videos for all available languages.Handles multi-language video transcripts seamlessly.

2)Language Detection and Translation:
Automatically detects the language of the transcript.Translates the transcript to English (default) or the selected target language.

3)Summary Generation:
Summarizes the transcript using Google Generative AI (Gemini Pro model).Offers customizable summary length as a percentage of the original content.

4)Customizable Summary Language:
Translates the summary to various target languages, including French, German, Spanish, Hindi, Telugu, Tamil, Malayalam,Kannada etc.

5)Video Details and Visualization:
Displays the video thumbnail and title for better context.

6)Download Summary:
Allows users to download the generated summary as a .txt file.

7)Custom UI Design:
Styled with CSS for animations and an appealing user interface using Instagram palette colors.




Project Structure :

Environment Setup:
API keys are stored in a .env file and loaded using the dotenv package.

Key Libraries Used:
streamlit: For building the interactive UI.
google.generativeai: For summary generation using the Gemini Pro model.
youtube_transcript_api: For fetching transcripts.
googletrans: For translation services.
langdetect: For detecting the language of the transcript.




How It Works
1. Enter Video Link:
Users input a YouTube video URL.
2. Transcript Extraction:
The YouTubeTranscriptApi fetches the transcript in all available languages.
Transcripts are concatenated to create a full text.
3. Language Detection and Translation:
The transcript's language is detected using langdetect.
If necessary, the transcript is translated into English for summary generation.
4. Summary Generation:
A custom prompt guides the Gemini Pro model to generate a concise summary.
Users can adjust the summary length using a slider.
5. Translation to Target Language:
The summary is translated into the selected target language.
6. Results Display and Download:
The summary is displayed alongside the video thumbnail and title.
A download button allows users to save the summary as a .txt file.
