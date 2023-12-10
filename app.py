import streamlit as st
import openai
import datetime
import os
import scipy.io.wavfile
from transformers import pipeline
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#openai

open_AI_key = os.environ.get('OPENAI_API_KEY')

# Function to extract mood from text using OpenAI
def extract_mood(user_input):
    openai.api_key = open_AI_key

    try:
        prompt = (
            "Based on the following user input, suggest a single mood keyword for a Spotify song. "
            "If the input suggests a negative or tired mood, suggest a mood that's relaxing "
            "Essentially, suggest a song that is positive if user input is negative and also helps the user"
            "If the input is positive, suggest a mood that maintains the positivity:\n\n"
            f"{user_input}"
        )
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=5
        )
        mood = response.choices[0].text.strip().lower()
        return mood
    except Exception as e:
        st.error("Error in OpenAI API call for mood extraction: " + str(e))
        return 'neutral'

# Function to get Spotify song suggestion
def get_spotify_song(mood):
    spotify_client_id = '1effb3e792d34d829ba1b7598457f292'
    spotify_client_secret = 'a4a2b0d29efd4036819712b13c61f7f1'
    client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    results = sp.search(q=mood, limit=1, type='track')
    track = results['tracks']['items'][0] if results['tracks']['items'] else None

    if track:
        track_url = track['external_urls']['spotify']
        track_name = track['name']
        st.write(f"Suggested Song: [{track_name}]({track_url})")
        st.markdown(f"<iframe src='https://open.spotify.com/embed/track/{track['id']}' width='300' height='380' frameborder='0' allowtransparency='true' allow='encrypted-media'></iframe>", unsafe_allow_html=True)

        # Steph added feature
        # Add like and dislike buttons
        # Add heart (like) and thumbs-down (dislike) buttons
        if st.button("❤️ Like"):
            st.write(f"You liked the song: {track_name}")
        if st.button("👎 Dislike"):
            st.write(f"You disliked the song: {track_name}")

# Function to generate a new song
def generate_new_song(user_input):
    openai.api_key = open_AI_key

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=(
                "Generate a text based on what this person's activity shows. "
                "If it has a negative implication, suggest a positive statement "
                "to help and encourage them to recover from the negative situation.\n"
                f"Response: {user_input}"
            ),
            max_tokens=50
        )
        result_text = response.choices[0].text.strip()
    except Exception as e:
        st.error("Error in OpenAI API call: " + str(e))
        return

    synthesiser = pipeline("text-to-audio", "facebook/musicgen-small")

    try:
        music = synthesiser(result_text, forward_params={"do_sample": True, "max_length": 100, "min_length": 50})
        scipy.io.wavfile.write("musicgen_out.wav", rate=music["sampling_rate"], data=music["audio"])
        st.audio("musicgen_out.wav", format='audio/wav')

        # Steph added feature
        # Add like and dislike buttons
        # Add heart (like) and thumbs-down (dislike) buttons
        if st.button("❤️ Like"):
            st.write(f"You liked the song")
        if st.button("👎 Dislike"):
            st.write(f"You disliked the song")
    except Exception as e:
        st.error("Error in audio generation: " + str(e))

# Streamlit App main function
def main():
    st.title("Bruce Almighty - Feel Better")

    # User choice for Sleep or Fatigue data
    data_choice = st.radio("Choose the type of data you want to enter:", ["Sleep", "Fatigue"])

    user_input = ""
    if data_choice == "Sleep":
        st.subheader("Sleep Data Information")
        pressure_intensity = st.slider("Stress Level", min_value=0, max_value=10, value=5)
        quality_of_sleep = st.slider("Quality of sleep", min_value=0, max_value=10, value=6)
        sleep_duration = st.text_input("Sleep Duration", value='6.2')
        sleep_disorder_choice = st.radio("Sleep Disorder", ["Yes", "No"])
        notes = st.text_area("Notes", value='I feel tired and need to relax during sleep.')
        user_input = f"Stress Level: {pressure_intensity}, Quality of Sleep: {quality_of_sleep}, Sleep Duration: {sleep_duration}, Sleep Disorder: {sleep_disorder_choice}, Notes: {notes}"


    elif data_choice == "Fatigue":
        st.subheader("Fatigue Data Information")
        # Fields for Fatigue Data (as provided)
        activity_date = st.date_input("Activity Date", datetime.date(2023, 10, 29))
        start_time = st.text_input("Start Time", value='08:00:00')  # Early start
        end_time = st.text_input("End Time", value='20:00:00')  # Long day
        activity_type = st.text_input("Type", value='Running')  # More strenuous than walking
        duration = st.text_input("Duration (seconds)", value='36000')  # Longer duration
        distance = st.text_input("Distance (meters)", value='10000')  # Greater distance
        calories_burned = st.text_input("Calories Burned", value='1000')  # Higher calorie burn
        avg_heart_rate = st.text_input("Average Heart Rate", value='120')  # Elevated heart rate
        peak_heart_rate = st.text_input("Peak Heart Rate", value='160')  # Higher peak heart rate
        steps = st.text_input("Steps", value='20000')  # More steps
        notes = st.text_area("Notes", value='I feel extremely fatigued, my muscles are sore, and I have low energy.')
        user_input = f"""
            Activity Date: {activity_date}
            Start Time: {start_time}
            End Time: {end_time}
            Type: {activity_type}
            Duration: {duration}
            Distance: {distance}
            Calories Burned: {calories_burned}
            Average Heart Rate: {avg_heart_rate}
            Peak Heart Rate: {peak_heart_rate}
            Steps: {steps}
            Notes: {notes}
            """

    choice = st.selectbox("Choose an option", [ "Get a Song Suggestion from Spotify","Generate a New Song"])

    if st.button("Proceed"):
        if choice == "Generate a New Song":
            generate_new_song(user_input)
        elif choice == "Get a Song Suggestion from Spotify":
            mood = extract_mood(user_input)
            get_spotify_song(mood)

if __name__ == "__main__":
    main()
