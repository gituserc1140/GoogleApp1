import streamlit as st
import google.generativeai as genai

# Initialize session state for API key
if 'api_key' not in st.session_state:
    st.session_state.api_key = None

def main():
    st.title("Google AI Studio API Key Input")

    # Input field for API key
    api_key_input = st.text_input("Enter your Google AI Studio API Key:", type="password")

    if api_key_input:
        st.session_state.api_key = api_key_input
        st.success("API Key saved successfully!")

    if st.session_state.api_key:
        genai.configure(api_key=st.session_state.api_key)
        st.write("API Key is configured. You can now use Google AI Studio APIs.")

        # Example usage of Google AI Studio API
        if st.button("Generate Text"):
            try:
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content("Hello, how are you?")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    main()