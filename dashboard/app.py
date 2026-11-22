import streamlit as st

st.set_page_config(layout="wide")

page = st.navigation([
    st.Page("what_happened.py", title="What Happened?"),
    st.Page("predictions.py", title="How Good are the Predictions?"),
    st.Page("what_to_do.py", title="What Should we Do?")
])

page.run()