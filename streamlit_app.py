import streamlit as st
import replicate
import os

# Fungsi untuk memuat token dari file atau variabel konfigurasi
def load_replicate_api_token():
    if 'REPLICATE_API_TOKEN' in st.secrets:
        return st.secrets['REPLICATE_API_TOKEN']
    else:
        return None

# Memuat Replicate API token
replicate_api = load_replicate_api_token()

# App title
st.set_page_config(page_title="NutriVeggie Chatbot 🤖")

# Replicate Credentials
with st.sidebar:
    st.title('NutriVeggie Chatbot 🤖')
    if replicate_api:
        st.success('')
    else:
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')
            # Menyimpan token di secrets
            st.secrets['REPLICATE_API_TOKEN'] = replicate_api
            # Menyimpan token di environment variable
            os.environ['REPLICATE_API_TOKEN'] = replicate_api

    st.subheader('Parameters')
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=0, max_value=500, value=250, step=8)

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Halo! Selamat datang di NutriVeggie Chatbot 🤖. Silakan berikan pertanyaan seputar sayuran, nutrisi, atau dunia vegetarian 🥦🥕🍅"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Halo! Selamat datang di NutriVeggie Chatbot 🤖. Silakan berikan pertanyaan seputar sayuran, nutrisi, atau dunia vegetarian 🥦🥕🍅"}]
st.sidebar.button('Hapus Pencarian', on_click=clear_chat_history)

# Function for generating LLaMA2 response.
def generate_llama2_response(prompt_input):
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run('meta/llama-2-13b-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5',
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature":temperature, "top_p":top_p, "max_length":max_length, "repetition_penalty":1})
    return output

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if the last message is not from the assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Loading..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
