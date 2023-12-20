import streamlit as st
import time
import os
from openai import OpenAI
from dotenv import find_dotenv, load_dotenv


st.title("💬 AI İnterviewer Resume")

if 'client' not in st.session_state:
    st.session_state.client = OpenAI(api_key="your key is here !")

if 'file' not in st.session_state:
    st.session_state.file = None

st.session_state.uploaded_file = st.file_uploader("Select the resume file", type=["pdf"])

if st.session_state.uploaded_file is not None:
    st.session_state.file = st.session_state.client.files.create(
        file=st.session_state.uploaded_file.read(),
        purpose="assistants"
    )

if st.button("Upload the resume"):
    if st.session_state.file is not None:
        st.session_state.assistant = st.session_state.client.beta.assistants.create(
            name="Resume Analyst",
            instructions="""You are a resume checker for Data Analyst. Use the following step-by-step instructions to respond to user inputs.
                             Step-1: Welcome the user and ask how they are today.
                             Step-2: Check if the user uploaded their resume file. If uploaded, start the evaluation process according to the instructions in Step-3.
                             Step-3: Start evaluating the resume according to the following sections: Personal information, Educational information, Work/Internship experience, Skills, Activities. Go to Step-4.
                             Step-4: If there are sections that we specified in Step-3, evaluate the content of the sections according to the data analyst resume.
                             Step-5: Give the user feedback at the end of the evaluation. The content of the feedback includes the following: What should be in the resume of a data analyst and why is it not in this resume. If there is a missing section in the resume, inform the user about it.""",
            model="gpt-3.5-turbo-1106",
            tools=[{"type": "retrieval"}],
            file_ids=[st.session_state.file.id]
        )
        st.session_state.thread = st.session_state.client.beta.threads.create()
        st.write("Your resume is ready for the assistant review.")
