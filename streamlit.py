import streamlit as st
import streamlit.components.v1 as components
import tools as tl

calendar_html = """
<iframe src="https://calendar.google.com/calendar/embed?height=600&wkst=1&ctz=America%2FNew_York&showPrint=0&mode=AGENDA&showTabs=0&showTitle=0&showNav=0&src=cnVzc2VsbGRheTQyMkBnbWFpbC5jb20&src=YWRkcmVzc2Jvb2sjY29udGFjdHNAZ3JvdXAudi5jYWxlbmRhci5nb29nbGUuY29t&src=NGE0OWViMGJlMDgzZDI2ZjkwMTg0YWMyMDA4YzM3N2I2ZjFlNmNjOTM0ODJiNTM0YTExNDAzZjNiODgyZTMwMkBncm91cC5jYWxlbmRhci5nb29nbGUuY29t&color=%23039BE5&color=%2333B679&color=%23EF6C00" style="border:solid 1px #777" width="800" height="600" frameborder="0" scrolling="no"></iframe>"""

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
