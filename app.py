import streamlit as st
import pylast

try:
    API_KEY = st.secrets["lastfm_api_key"]
    API_SECRET = st.secrets["lastfm_api_secret"]
    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)
except Exception:
    st.error("API Keys are missing in Streamlit Secrets! Check your dashboard.")
    st.stop()

st.set_page_config(page_title="Che Listening Tracker", page_icon="🐰")
st.title("🐰Che Listening History")
st.write("Calculate your total hours and see your top songs for **Che**.")

username = st.text_input("Enter Last.fm Username", placeholder="e.g. chefan123")

if st.button("Track Che Stats"):
    if username:
        try:
            with st.spinner(f"🔍 Analyzing {username}'s library...this may take a while."):
                
                user = network.get_user(username)
                top_tracks = user.get_top_tracks(period=pylast.PERIOD_OVERALL, limit=1000)
                
                che_tracks = []
                total_seconds = 0
                
                for item in top_tracks:
                    track = item.item
                    if "che" in track.artist.name.lower():
                        playcount = int(item.weight)
                        
                        duration = track.get_duration()
                        if not duration or duration <= 0:
                            duration = 135000 
                        
                        song_seconds = (playcount * (duration / 1000))
                        total_seconds += song_seconds
                        
                        che_tracks.append({
                            "Song": track.title,
                            "Streams": playcount,
                            "Minutes": int(song_seconds // 60)
                        })
                
                che_tracks = sorted(che_tracks, key=lambda x: x['Minutes'], reverse=True)

            if che_tracks:
                total_mins = int(total_seconds // 60)
                total_hrs = round(total_seconds / 3600, 1)

                st.divider()
                st.header("🏆 Your Che Stats")
                
                col1, col2 = st.columns(2)
                col1.metric("Total Time (Minutes)", f"{total_mins:,}")
                col2.metric("Total Time (Hours)", f"{total_hrs:,}")
                
                st.write(f"Stats based on your top {len(top_tracks)} tracks overall.")
                st.divider()

                with st.expander("💿 View your Top 100 Che Songs"):
                    st.info("Ranked by Total Minutes")
                    for i, song in enumerate(che_tracks[:100], 1):
                        st.write(f"{i}. **{song['Song']}** — {song['Streams']} streams — {song['Minutes']} mins")
                
                st.balloons() 

            else:
                st.warning(f"No songs by 'Che' were found in the top 1000 tracks for {username}.")

        except Exception as e:
            st.error(f"Something went wrong! Error: {e}")
    else:
        st.info("Enter your username above and click the button to see your stats.")
