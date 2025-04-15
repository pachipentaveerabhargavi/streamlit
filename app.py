import streamlit as st
import requests
import re
import json

def extract_username(profile_url):
    match = re.search(r"leetcode\.com/([^/]+)/?", profile_url)
    if match:
        username = match.group(1)
        # Ignore 'problems', 'contest', etc.
        if username in ["problems", "contest", "discuss", "explore", "studyplan"]:
            return None
        return username
    return None

def get_user_stats(username):
    url = "https://leetcode.com/graphql"
    query = {
        "operationName": "getUserProfile",
        "variables": {"username": username},
        "query": """
        query getUserProfile($username: String!) {
          matchedUser(username: $username) {
            submitStats {
              acSubmissionNum {
                difficulty
                count
              }
            }
          }
        }
        """
    }

    headers = {
        "Content-Type": "application/json",
        "Referer": f"https://leetcode.com/{username}/"
    }

    response = requests.post(url, headers=headers, json=query)
    if response.status_code == 200:
        data = response.json()
        stats = data["data"]["matchedUser"]
        if stats:
            ac_data = stats["submitStats"]["acSubmissionNum"]
            result = {entry["difficulty"]: entry["count"] for entry in ac_data}
            return {
                "Easy": result.get("Easy", 0),
                "Medium": result.get("Medium", 0),
                "Hard": result.get("Hard", 0),
                "Total": result.get("All", 0)
            }
    return None

# Streamlit App
st.title("📊 LeetCode Profile Analyzer")
st.write("Enter a LeetCode user profile URL to get the number of solved problems by difficulty.")

profile_url = st.text_input("Enter LeetCode profile URL (e.g. https://leetcode.com/johndoe/)")

if profile_url:
    username = extract_username(profile_url)
    if not username:
        st.error("❌ Could not extract a valid username from the URL.")
    else:
        with st.spinner(f"Fetching data for user `{username}`..."):
            stats = get_user_stats(username)
        
        if stats:
            st.success(f"✅ Data fetched for `{username}`")
            st.json(stats)

            # Create downloadable JSON file
            json_data = json.dumps(stats, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"{username}_leetcode_stats.json",
                mime="application/json"
            )
        else:
            st.error("⚠️ Could not fetch stats. The profile might be private or invalid.")
