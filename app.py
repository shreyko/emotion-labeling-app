import streamlit as st
import pandas as pd
import uuid
import random
import gspread

DATASET_FILE = "data/emotion_dataset_50.csv"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'assigned_tweets' not in st.session_state:
    st.session_state.assigned_tweets = None
if 'page' not in st.session_state:
    st.session_state.page = "auth"

@st.cache_resource
def get_gspread_client():
    credentials_dict = dict(st.secrets["connections"]["gsheets"])
    if "spreadsheet" in credentials_dict:
        del credentials_dict["spreadsheet"]
    
    gc = gspread.service_account_from_dict(credentials_dict)
    sh = gc.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
    return sh

def get_sheet_data(worksheet_name):
    sh = get_gspread_client()
    worksheet = sh.worksheet(worksheet_name)
    records = worksheet.get_all_records()
    return pd.DataFrame(records)

@st.cache_data
def load_tweets():
    try:
        return pd.read_csv(DATASET_FILE)
    except FileNotFoundError:
        return None

def login_signup_page():
    st.title("Emotion Labeling Task")
    st.write("Welcome to the Emotion Data Labeling portal.")
    
    tab1, tab2 = st.tabs(["Log In", "Sign Up"])
    
    with tab1:
        st.subheader("Log In")
        email_in = st.text_input("Email", key="log_email")
        pass_in = st.text_input("Password", type="password", key="log_pass")
        
        if st.button("Log In"):
            users_df = get_sheet_data("Users")
            if not users_df.empty:
                users_df['email'] = users_df['email'].astype(str)
                users_df['password'] = users_df['password'].astype(str)
                user = users_df[(users_df['email'] == email_in) & (users_df['password'] == pass_in)]
            else:
                user = pd.DataFrame()
            
            if not user.empty:
                current_user_id = user.iloc[0]['user_id']
                st.session_state.logged_in = True
                st.session_state.user_id = current_user_id
                
                annotations_df = get_sheet_data("Annotations")
                if not annotations_df.empty and 'user_id' in annotations_df.columns:
                    annotations_df['user_id'] = annotations_df['user_id'].astype(str)
                    if str(current_user_id) in annotations_df['user_id'].values:
                        st.session_state.page = "already_completed"
                        st.rerun()
                        return
                
                st.session_state.page = "labeling"
                st.rerun()
            else:
                st.error("Invalid email or password.")

    with tab2:
        st.subheader("Sign Up")
        name_up = st.text_input("Full Name")
        email_up = st.text_input("Email", key="sign_email")
        pass_up = st.text_input("Password", type="password", key="sign_pass")
        
        if st.button("Create Account"):
            users_df = get_sheet_data("Users")
            
            if not users_df.empty and email_up in users_df['email'].astype(str).values:
                st.error("Email already registered. Please log in.")
            elif name_up and email_up and pass_up:
                new_id = str(uuid.uuid4())
                
                sh = get_gspread_client()
                users_sheet = sh.worksheet("Users")
                users_sheet.append_row([new_id, name_up, email_up, pass_up])
                
                st.success("Account created! Please switch to the Log In tab.")
            else:
                st.error("Please fill in all fields.")

def labeling_page():
    st.title("Emotion Labeling Task")
    st.write("### Instructions")
    st.write("Please read each tweet below carefully. Select the emotion that best represents the feeling expressed in the text. You have been assigned 5 tweets to label.")
    st.divider()

    tweets_df = load_tweets()
    if tweets_df is None:
        st.error(f"Dataset not found! Please make sure {DATASET_FILE} exists.")
        return

    if st.session_state.assigned_tweets is None:
        st.session_state.assigned_tweets = tweets_df.sample(n=5).to_dict('records')

    emotions = ["anger", "fear", "joy", "love", "sadness", "surprise"]
    
    with st.form("labeling_form"):
        responses = []
        for i, tweet in enumerate(st.session_state.assigned_tweets):
            st.write(f"**Tweet {i+1}:** {tweet['text']}")
            choice = st.radio(
                "Select Emotion:",
                options=emotions,
                key=f"tweet_{tweet['tweet_id']}",
                horizontal=True,
                index=None
            )
            responses.append([
                st.session_state.user_id,
                tweet['tweet_id'],
                tweet['text'],
                choice
            ])
            st.write("---")
            
        submitted = st.form_submit_button("Submit Annotations")
        
        if submitted:
            if any(resp[3] is None for resp in responses):
                st.error("Please select an emotion for all 5 tweets before submitting.")
                return
                
            sh = get_gspread_client()
            annotations_sheet = sh.worksheet("Annotations")
            annotations_sheet.append_rows(responses)
            
            st.session_state.page = "thanks"
            st.rerun()

def thanks_page():
    st.title("Task Complete!")
    st.success("Thank you for your time. Your responses have been successfully recorded in our database.")
    st.balloons()
    st.write("You may now close this window, or log out.")
    
    if st.button("Log Out"):
        st.session_state.clear()
        st.session_state.page = "auth"
        st.rerun()

def already_completed_page():
    st.title("Task Already Completed")
    st.warning("Welcome back! Our records indicate that you have already submitted your 5 annotations for this study.")
    st.write("To preserve data integrity, participants are only allowed to complete the task once. Thank you for your contribution!")
    
    if st.button("Log Out"):
        st.session_state.clear()
        st.session_state.page = "auth"
        st.rerun()

if st.session_state.page == "auth":
    login_signup_page()
elif st.session_state.page == "labeling":
    labeling_page()
elif st.session_state.page == "thanks":
    thanks_page()
elif st.session_state.page == "already_completed":
    already_completed_page()
