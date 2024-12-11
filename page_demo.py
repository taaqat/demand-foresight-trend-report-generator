import streamlit as st

st.title("DEMO")





steep, self_select, archive = st.tabs(['STEEP +B', '自選主題', 'ARCHIVE'])

with steep:
    with st.container(border = True):
        st.video("https://www.youtube.com/watch?v=_HAff6tZ9hU")

with self_select:
    with st.container(border = True):
        st.video("https://www.youtube.com/watch?v=VEMfloptbw8")

with archive:
    with st.container(border = True):
        st.video("https://www.youtube.com/watch?v=ibwSk1mbQ1k")