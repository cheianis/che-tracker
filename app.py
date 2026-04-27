import streamlit as st
import pylast

# 1. Secure Setup (We will add these keys in Step 5)
try:
    API_KEY = st.secrets["lastfm_api_key"]
    API_SECRET = st.secrets["lastfm_api_secret"]
    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)
except:
    st.error("API Keys missing! Add them in Streamlit Secrets.")

st.title("🐰Che Listening History")

# 2. User Input
username = st.text_input("Enter Last.fm Username", placeholder="e.g. chefan123")

if st.button("Track Che Stats"):
    if username:
        try:
            user = network.get_user(username)
            with st.spinner("Scanning your library..."):
                # limit=1000 ensures we catch all your Che plays
                top_tracks = user.get_top_tracks(period=pylast.PERIOD_OVERALL, limit=1000)
            
            che_tracks = []
            total_seconds = 0
            
            for item in top_tracks:
                track = item.item
                if track.artist.name.lower() == "che":
                    playcount = int(item.weight)
                    duration = track.get_duration() or 135000 # 2:15 fallback
                    
                    song_seconds = (playcount * (duration / 1000))
                    total_seconds += song_seconds
                    
                    che_tracks.append({
                        "Song": track.title,
                        "Streams": playcount,
                        "Minutes": int(song_seconds // 60)
                    })

            if che_tracks:
                # Show the List
                for i, song in enumerate(che_tracks[:100], 1):
                    st.write(f"{i}. **{song['Song']}** — {song['Streams']} streams — {song['Minutes']} mins")
                
                # Show the Grand Total
                st.divider()
                st.header(f"Total Che Time: {int(total_seconds // 60)} Minutes")
                st.subheader(f"({round(total_seconds / 3600, 1)} Hours)")
            else:
                st.warning("No Che songs found in your top 1000 tracks!")
        except Exception as e:
            st.error(f"User not found or API error: {e}")
