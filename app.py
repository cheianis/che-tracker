import streamlit as st
import pylast

# --- 1. SECURE SETUP ---
# Ensure these names match your "Advanced Settings > Secrets" in Streamlit
try:
    API_KEY = st.secrets["lastfm_api_key"]
    API_SECRET = st.secrets["lastfm_api_secret"]
    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)
except Exception as e:
    st.error("API Keys are missing in Streamlit Secrets!")
    st.stop()

# --- 2. WEB UI HEADER ---
st.set_page_config(page_title="Che Listening Tracker", page_icon="⚖️")
st.title("🐰Che Listening History")
st.write("Track your total hours and top songs for **Che**.")

# User Input Section
username = st.text_input("Enter Last.fm Username", placeholder="e.g. chefan123")

if st.button("Track Stats"):
    if username:
        try:
            user = network.get_user(username)
            with st.spinner("Analyzing your library... this takes a moment for heavy listeners!"):
                # Fetching top 1000 tracks to ensure we catch the 350+ hour stats
                top_tracks = user.get_top_tracks(period=pylast.PERIOD_OVERALL, limit=1000)
            
            che_tracks = []
            total_seconds = 0
            
            # --- 3. THE MATH (Done in the background) ---
            for item in top_tracks:
                track = item.item
                # Improved filter to catch "Che", "CHE", "ché", etc.
                if "che" in track.artist.name.lower():
                    playcount = int(item.weight)
                    
                    # Duration logic
                    duration = track.get_duration()
                    if not duration or duration <= 0:
                        duration = 135000 # 2:15 average for Che tracks
                    
                    song_seconds = (playcount * (duration / 1000))
                    total_seconds += song_seconds
                    
                    che_tracks.append({
                        "Song": track.title,
                        "Streams": playcount,
                        "Minutes": int(song_seconds // 60)
                    })

            # --- 4. DISPLAY RESULTS (Total First!) ---
            if che_tracks:
                total_mins = int(total_seconds // 60)
                total_hrs = round(total_seconds / 3600, 1)

                st.divider()
                st.header("🏆 Your Che Stats")
                
                # Big Metric Cards at the Top
                col1, col2 = st.columns(2)
                col1.metric("Total Time (Minutes)", f"{total_mins:,}")
                col2.metric("Total Time (Hours)", f"{total_hrs:,}")
                
                st.write(f"Based on your top {len(top_tracks)} most played songs overall.")
                st.divider()

                # --- 5. THE EXPANDER (Songs Hidden inside) ---
                with st.expander("💿 View your Top 100 Che Songs"):
                    st.write("Ranking is based on Total Minutes (Streams × Duration)")
                    for i, song in enumerate(che_tracks[:100], 1):
                        st.write(f"{i}. **{song['Song']}** — {song['Streams']} streams — {song['Minutes']} mins")
                
                st.balloons() # Success animation!

            else:
                st.warning(f"No songs by 'Che' found in the top 1000 tracks for {username}. Try a different user!")

        except Exception as e:
            st.error(f"Error: Could not find user or API issue. ({e})")
    else:
        st.info("Please enter a username above to begin.")
