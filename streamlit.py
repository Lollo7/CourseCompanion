import streamlit as st
import streamlit.components.v1 as components
import tools as tl



def configurepage() -> None:
    st.set_page_config(page_title="Google Calendar API", page_icon=":calendar:", layout="centered", initial_sidebar_state="expanded")  


def configure_overview() -> None:
    st.markdown("### Hello WORLD")
    st.markdown("This is a simple Streamlit app that demonstrates how to use the Google Calendar API to list the upcoming events on your calendar.")

def main() -> None: 
    configurepage()
    configure_overview()
    st.markdown(tl.get_current_term())
    components.html(calendar_html, height=1000) 
    

if __name__ == "__main__":
    main()
