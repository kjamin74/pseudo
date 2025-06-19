import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# AS400 style CSS with blinking caret
as400_style = """
<style>
    html, body, .stApp {
        background-color: black !important;
        color: #00FF00 !important;
        font-family: 'Courier New', Courier, monospace !important;
        margin: 0; padding: 0; height: 100%;
    }
    .block-container {
        padding: 1rem 2rem !important;
        background-color: black !important;
    }
    .as400-input-row {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    div[data-baseweb="input"] {
        border: none !important;
        background-color: black !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    .stTextInput input {
        background-color: black !important;
        color: #00FF00 !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 16px !important;
        padding: 0 !important;
        height: auto !important;
        width: 100% !important;
        caret-color: #00FF00 !important;
        animation: blink-caret 1s step-start infinite;
    }
    .stTextInput input::placeholder {
        color: #00FF00 !important;
        opacity: 0.6;
    }
    .stMarkdown, .stWarning, .stText {
        color: #00FF00 !important;
        font-family: 'Courier New', Courier, monospace !important;
    }
    .hide-prompt {
        color: black !important;
    }

    @keyframes blink-caret {
        from, to { border-color: transparent; }
        50% { border-color: #00FF00; }
    }
</style>
"""
st.markdown(as400_style, unsafe_allow_html=True)

# Load CSVs
df_customer = pd.read_csv("Customer_names.csv")
df_customer.columns = df_customer.columns.str.lower()

df_rm = pd.read_csv("Customer_RM.csv")
df_rm.columns = df_rm.columns.str.strip().str.lower().str.replace(' ', '_')

# Initialize session state variables
if 'screen' not in st.session_state:
    st.session_state.screen = 'main'  # 'main', 'sub1', 'sub2'

if 'customer_id' not in st.session_state:
    st.session_state.customer_id = ""

if 'nav_input' not in st.session_state:
    st.session_state.nav_input = ""

if '_rerun' not in st.session_state:
    st.session_state._rerun = False

def force_rerun():
    st.session_state._rerun = not st.session_state._rerun

st.markdown("## IBM AS400 Terminal - Pseudo SIBS")

def on_customer_id_change():
    cid = st.session_state.customer_input.strip()
    if cid and cid != st.session_state.customer_id:
        if not df_customer[df_customer['id'].astype(str) == cid].empty:
            st.session_state.customer_id = cid
            st.session_state.screen = 'sub1'
            st.session_state.nav_input = ""
            force_rerun()
        else:
            st.warning("Customer ID not found.")

def on_nav_input_change():
    nav = st.session_state.nav_input.strip()
    if nav == "1":
        if st.session_state.screen == 'sub2':
            st.session_state.screen = 'sub1'
            st.session_state.nav_input = ""
            force_rerun()
        elif st.session_state.screen == 'sub1':
            st.session_state.screen = 'main'
            st.session_state.customer_id = ""
            st.session_state.nav_input = ""
            st.session_state['customer_input'] = ""
            force_rerun()
    elif nav == "2":
        if st.session_state.screen == 'sub1':
            st.session_state.screen = 'sub2'
        elif st.session_state.screen == 'sub2':
            st.session_state.screen = 'sub1'
        st.session_state.nav_input = ""
        force_rerun()

def set_focus_to_nav_delayed(key: str):
    # Focus with 100ms delay to ensure element exists in DOM
    js_code = f"""
    <script>
    setTimeout(() => {{
        const input = window.parent.document.querySelector('input[aria-label="{key}"]');
        if(input){{
            input.focus();
            input.select();
        }}
    }}, 100);
    </script>
    """
    components.html(js_code, height=0, width=0)

if st.session_state.screen == 'main':
    st.markdown('<div class="as400-input-row">', unsafe_allow_html=True)
    col1, col2 = st.columns([1.5,5])
    with col1:
        st.markdown("Enter Customer ID:")
    with col2:
        st.text_input("", key="customer_input", label_visibility="collapsed", on_change=on_customer_id_change)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.screen == 'sub1':
    st.markdown('<div class="as400-input-row">', unsafe_allow_html=True)
    col1, col2 = st.columns([2,6])
    with col1:
        st.markdown('<span class="hide-prompt">Enter Customer ID:</span>', unsafe_allow_html=True)        
    with col2:
        st.markdown("&nbsp;", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    cust = df_customer[df_customer['id'].astype(str) == st.session_state.customer_id]
    if not cust.empty:
        st.markdown(f"Customer ID: {st.session_state.customer_id}")
        st.markdown(f"Customer Name: {cust.iloc[0]['name']}")
    else:
        st.warning("Customer data missing.")

    st.markdown('<div class="as400-input-row">', unsafe_allow_html=True)
    col1, col2 = st.columns([1.5,3])
    with col1:
        st.markdown("Enter 1 for Previous, 2 for Next:")
    with col2:
        st.text_input("", key="nav_input", max_chars=1, label_visibility="collapsed", on_change=on_nav_input_change)
    st.markdown('</div>', unsafe_allow_html=True)

    set_focus_to_nav_delayed("nav_input")

elif st.session_state.screen == 'sub2':
    cust = df_customer[df_customer['id'].astype(str) == st.session_state.customer_id]
    rm = df_rm[df_rm['id'].astype(str) == st.session_state.customer_id]

    if not cust.empty:
        st.markdown(f"Customer Name: {cust.iloc[0]['name']}")
    else:
        st.warning("Customer data missing.")

    if not rm.empty and 'rm_code' in rm.columns:
        st.markdown(f"RM Code: {rm.iloc[0]['rm_code']}")
    else:
        st.warning("RM data missing.")

    st.markdown('<div class="as400-input-row">', unsafe_allow_html=True)
    col1, col2 = st.columns([1.5,3])
    with col1:
        st.markdown("Enter 1 for Previous, 2 for Next:")
    with col2:
        st.text_input("", key="nav_input", max_chars=1, label_visibility="collapsed", on_change=on_nav_input_change)
    st.markdown('</div>', unsafe_allow_html=True)

    set_focus_to_nav_delayed("nav_input")
