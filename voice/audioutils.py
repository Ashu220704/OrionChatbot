import os
import tempfile

def save_uploaded_audio(uploaded_audio):
    """
        Save streamlit uploaded file
        returns the temporary file path
    """

    temp_dir = "audio"

    os.makedirs(temp_dir, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        dir = temp_dir,
        suffix = ".wav",
        delete = False
    ) as temp_file:
        temp_file.write(uploaded_audio.read())
        return temp_file.name


def delete_audio(file_path):
    """
        Delete the temporary audio file
    """

    if os.path.exists(file_path):
        os.remove(file_path)