import streamlit as st
import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator import Hasher
from managers.session_manager import SessionManager

# *********** Config ***********
if "config" not in st.session_state:
    with open("users.yaml") as file:
        st.session_state.config = yaml.load(file, Loader=SafeLoader)

# button style setting
st.markdown("""<style>
div.stButton > button {
    width: 100%;  /* 設置按鈕寬度為頁面寬度的 50% */
    height: 50px;
    margin-left: 0;
    margin-right: auto;
}
</style>
""", unsafe_allow_html=True)


# *** entry point after login ***
def main():
    st.session_state['logged_in'] = True

    st.sidebar.header("資策會 Demand Foresight Tools")
    with st.sidebar:
        st.page_link('index.py', label = 'Home Page', icon = ':material/add_circle:')

    st.sidebar.write("**趨勢報告產生器**")
    with st.sidebar:
        st.page_link('pages/page_demo.py', label = 'DEMO Videos', icon = ':material/add_circle:')
        st.page_link('pages/page_steep.py', label = 'STEEP +B 月報', icon = ':material/add_circle:')
        st.page_link('pages/page_self_select.py', label = '自選主題', icon = ':material/add_circle:')
        st.page_link('pages/page_archive.py', label = 'ARCHIVE', icon = ':material/add_circle:')


    st.sidebar.write("**對話式工具**")
    st.sidebar.page_link("https://livinglab-demand-foresight-chat.streamlit.app/", label = "RAG 與文件對話", icon = ':material/link:')
    
    st.sidebar.write("**視覺化界面**")
    # st.sidebar.page_link("[小賴做的視覺化界面]", label = "", icon = ':material/add_circle:')
    

    with st.container(border = True):
        st.markdown("[![Foo](http://www.google.com.au/images/nav_logo7.png)](http://google.com.au/)")

    

    

# *** 目前因為我改了 navigation bar 的設定（是用自己設定的 page_link 設定），當 app 開啟後連入此 py 檔，會立刻導向 page_demo.py！
# *** Authentication 邏輯因此遇到設計上的問題，先不處理
    
# *** Authentication ***

authenticator = stauth.Authenticate(
    st.session_state.config['credentials'],
    st.session_state.config['cookie']['name'],
    st.session_state.config['cookie']['key'],
    st.session_state.config['cookie']['expiry_days'],
)
try:
    l, m, r = st.columns((1/4, 1/2, 1/4))
    with m:
        placeholder = st.container()
    with placeholder:
        authenticator.login('main')
except Exception as e:
    st.error(e)

if st.session_state.authentication_status:
    st.session_state.authenticator = authenticator
    main()
    with st.sidebar:
        authenticator.logout()
elif st.session_state.authentication_status is False:
    st.error('使用者名稱/密碼不正確')


