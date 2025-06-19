import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
import google.api_core.exceptions # Import the exceptions module

# Load environment variables
load_dotenv()

# Configure Generative AI with API key
# Ensure GOOGLE_API_KEY is set in your .env file
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("Google API Key not found. Please set the GOOGLE_API_KEY environment variable in your .env file.")
    st.stop() # Stop the app if API key is missing

genai.configure(api_key=api_key)

# Function to get Gemini response
def get_gemini_repsonse(input_text, image_parts, prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Ensure image_parts is a list of dictionaries as expected by the model
        response = model.generate_content([input_text, image_parts[0], prompt])
        return response.text
    except google.api_core.exceptions.InvalidArgument as e:
        st.error(f"Invalid argument error from Gemini API: {e}. This might indicate an issue with the prompt or image data.")
        return None
    except google.api_core.exceptions.FailedPrecondition as e:
        st.error(f"Failed precondition error from Gemini API: {e}. This can happen if the model is not available or if there's an issue with the request setup.")
        return None
    except google.api_core.exceptions.ResourceExhausted as e:
        st.error(f"Quota exceeded error from Gemini API: {e}. You might have hit your usage limits. Please check your Google Cloud Console for details.")
        return None
    except google.api_core.exceptions.DeadlineExceeded as e:
        st.error(f"API call timed out: {e}. This might be due to network issues or slow model response.")
        return None
    except google.api_core.exceptions.GoogleAPICallError as e:
        st.error(f"An error occurred with the Gemini API call: {e}. Please check your API key and network connection.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}. Please try again.")
        return None

# Function to prepare image for Gemini
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Define the input prompt for image captioning
input_prompt = """You are an expert image captioning so whatever image you will get give a suitable caption in one phrase."""

# Streamlit UI
st.set_page_config(page_title="IMAGE CAPTIONING")

st.header("IMAGE TO CAPTION")

# Input prompt from user (can be left empty if not used for the specific task)
user_input_text = st.text_input("Additional Context/Prompt (Optional):", key="input")

# Image uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

image = None # Initialize image to None
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

# Submit button
submit = st.button("Generate Caption")

# When submit button is clicked
if submit:
    if uploaded_file is not None:
        try:
            image_data = input_image_setup(uploaded_file)
            # Pass the user_input_text as the 'input' argument to the model.
            # The main instruction for captioning comes from input_prompt.
            response_text = get_gemini_repsonse(user_input_text, image_data, input_prompt)
            if response_text:
                st.subheader("The Caption Is:")
                st.write(response_text)
        except FileNotFoundError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"An error occurred during image processing: {e}")
    else:
        st.warning("Please upload an image first to generate a caption!")