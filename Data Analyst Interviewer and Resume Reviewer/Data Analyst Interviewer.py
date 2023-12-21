import openai
import time
import streamlit as st
import os
import pandas as pd

os.environ["OPENAI_API_KEY"] ="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"

# note: you will have to change api key and file id (of csv file)

def main():
    in_progress_counter = 0
    st.title("💬 Interview Chatbot")
    if 'file' not in st.session_state:
        st.session_state.file = None
    
    file = open('/Users/yunsemr/Downloads/ai_interview_data_1.csv', 'rb')


    if 'client' not in st.session_state:
        # Initialize the client
        st.session_state.client = openai.OpenAI()
        
        st.session_state.file = st.session_state.client.files.create(
            file = file,
            purpose="assistants"
        )

        # Step 1: Create an Assistant
        st.session_state.assistant = st.session_state.client.beta.assistants.create(
            name="Data Analyst Interviewer",
            instructions="""You are a data analyst interviewer, you will make a data analyst interview simulation with the user, use the following steps to make data analyst interview: \n  
                            step 1 - welcome the user, ask user their name. Do not talk about this file to the user. then go step 2 \n
                            step 2- only choose and randomly from the file ai_interview_data_1.csv. Do not talk about this file to the user. Choose three questions which have a difficulty of Easy. Choose four questions which have a difficulty of Normal. Choose three questions which have a difficulty of Hard. Save these questions to the memmory. Do not show the whole questions in once. Go to the step 3. \n
                            step 3 - Ask these question one by one. First ask Easy questions then Normal Questions, then Hard questions. After the user gives answer check whether answer is correct or not. If answer is wrong or user does not know the answer, then give a very brief hint to the user only once and wait for answer. Then, depending on the how correct the answer is, give a point out of 100 for answers and save this point in the memory and do not tell the score to the user. Then go to step 4. \n 
                            step 4 - After getting the last answer, finish the session. Show show the average point and each points for each questions. Then tell weaknesses and strengths of the user according to the answers.""",
            model="gpt-3.5-turbo-1106",
            tools=[{"type": "code_interpreter"}],
            file_ids= [st.session_state.file.id]
        )

        # Step 2: Create a Thread
        st.session_state.thread = st.session_state.client.beta.threads.create()

    
    
    if user_query := st.chat_input():
        # Step 3: Add a Message to a Thread
        message = st.session_state.client.beta.threads.messages.create(
            thread_id=st.session_state.thread.id,
            role="user",
            content=user_query
        )

        # Step 4: Run the Assistant
        run = st.session_state.client.beta.threads.runs.create(
            thread_id=st.session_state.thread.id,
            assistant_id=st.session_state.assistant.id,
        )

        while True:
            
            # Retrieve the run status
            run_status = st.session_state.client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread.id,
                run_id=run.id
            )
            if run_status.status == 'in_progress':
                in_progress_counter += 1
            
            if in_progress_counter == 1:
                # get history
                messages = st.session_state.client.beta.threads.messages.list(
                        thread_id=st.session_state.thread.id
                )

                messages.data.reverse()

                # print history
                for msg in messages.data: 
                    role = msg.role
                    content = msg.content[0].text.value
                    st.chat_message(role.capitalize()).write(content)

            # Wait for 5 seconds
            time.sleep(5)

            # Retrieve the run status
            run_status = st.session_state.client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread.id,
                run_id=run.id
            )

            # If run is completed, get message
            if run_status.status == 'completed':
                messages = st.session_state.client.beta.threads.messages.list(
                    thread_id=st.session_state.thread.id
                )
                in_progress_counter = 0

                # get response
                for msg in messages.data:
                    role = msg.role
                    content = msg.content[0].text.value
                    st.chat_message(role.capitalize()).write(content)
                    break
                break

            elif run_status.status == 'failed':
                "There is an error. Please write OK!"
                break
            else:
                st.write("Waiting for the Assistant to process...")
                time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except Exception as e: 
        print(e)