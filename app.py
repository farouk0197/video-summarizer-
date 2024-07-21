import streamlit as st
import os
import openai
from openai import OpenAI
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube

def get_youtube_video_info(youtube_video_url):

    yt = YouTube(youtube_video_url)

    video_details = {
        "title": yt.title,
        "description" : yt.description,
        "views" : yt.views,
        "length": yt.length,
        "author": yt.author,
        "publish_date": yt.publish_date
    }


    try: 
        video_id = youtube_video_url.split("=")[1]
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id,languages=["en","fr","es"], preserve_formatting= True)
        transcript_text = " ".join([item["text"] for item in transcript_list])
        video_details["transcript"] = transcript_text
    except Exception as e:
        print(f"could not retive transcript: {e}")
        video_details["transcript"] = None

    return video_details



def generate_summary(transcript_text):


    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                { "role": "system", "content": f"You are a YouTube video summarizer.
                  Your task is to ananlyze the provided transript and condense it into
                  a clear and informative summary in {language}
                    language with upto 500 words or less"
                    }, {"role": "user", "content": transcript_text}
                    ],
                    max_tokens=300

        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating summary: {e}")

st.title("YouTube Video Summarizer App")

with st.form("youtube_form"):
    youtube_link = st.text_input("Enter Youtube Video Link:")
    language = st.selectbox("Select Language for Summary", ["English","French", "Spanish"])
    submit_button = st.form_submit_button("Summarize")


if submit_button and youtube_link:
    video_id = youtube_link.split("=")[1]
    st.image(f"hiit://img.youtube.com/vi/{video_id}/0.jpg", caption="Video Thumbnail", use_column_width=True)

    with st.spinner("Generating summary..."):
        video_info = get_youtube_video_info(youtube_link)
        if video_info['transcript']:
            summary = generate_summary(video_info["transcript"])

            if summary:
                st.subheader("Summary:")
                st.markdown(summary)
                st.subheader("Additional Info:")
                st.markdown(f"***Title:** {video_info.get("title","N/A")}")
                st.markdown(f"***Views:** {video_info.get("views","N/A")}")
                st.markdown(f"***Length (seconds):** {video_info.get("length","N/A")}")
                st.markdown(f"***Author:** {video_info.get("author","N/A")}")
                st.markdown(f"***Publish Date:** {video_info.get("publish_date","N/A")}")
            else:
                st.warning("Summary generation failed. Please try again of check the video link")

        else:
            st.error("Error extracting transcript.")