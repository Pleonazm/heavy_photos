from pathlib import Path
from typing import Union, Tuple
import requests
import base64
from io import BytesIO, BufferedReader
from dotenv import dotenv_values
from ai_client_wrapper import AI_Client_Call_Wrapper
import json
from ai_client_wrapper import AI_Client_Call_Wrapper


env = dotenv_values(".env")
ac3 = AI_Client_Call_Wrapper.make_from_key(api_key=env["OPENAI_API_KEY"])
ac = AI_Client_Call_Wrapper(api_key=env["OPENAI_API_KEY"])
ac2 = AI_Client_Call_Wrapper.make_from_key(api_key=env["OPENAI_API_KEY"])


def get_file_data(url: Union[str, Path]) -> Tuple[Union[BufferedReader, bytes], str]:
    """
    Retrieves file data from a local file path or a remote URL.

    Args:
        url (Union[str, Path]): The file path or URL.

    Returns:
        Tuple[Union[BufferedReader, bytes], str]: A tuple containing the file content (as an io.BufferedReader or bytes) and a description string.
    """
    content = None
    info = None

    if isinstance(url, Path) or (isinstance(url, str) and Path(url).is_file()):
        # Handle local file
        content = open(url, mode='rb')
        info = f'local file {url}'
    elif isinstance(url, str):
        # Handle remote URL
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful
        content = response.content
        info = f"remote file {url}"
    else:
        info = f'Wrong url: {url}'

    return content, info

def prepare_image_for_open_ai(image_input: Union[str, Path, BytesIO, BufferedReader, bytes], mime: str = 'image/png') -> str:
    """
    Prepares an image for OpenAI by encoding it as a base64 data URL.

    Args:
        image_input (Union[str, Path, BytesIO, BufferedReader, bytes]): The image input, which can be a file path (str or Path), a BytesIO object, an io.BufferedReader, or raw bytes.
        mime (str): The MIME type of the image (default is 'image/png').

    Returns:
        str: A base64-encoded data URL representing the image.
    """
    if isinstance(image_input, (str, Path)):
        # Handle file path (str or Path)
        with open(image_input, "rb") as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
    elif isinstance(image_input, BytesIO):
        # Handle BytesIO object
        image_data = base64.b64encode(image_input.getvalue()).decode('utf-8')
    elif isinstance(image_input, BufferedReader):
        # Handle io.BufferedReader object
        image_data = base64.b64encode(image_input.read()).decode('utf-8')
        image_input.seek(0)  # Reset the file pointer to the beginning
    elif isinstance(image_input, bytes):
        # Handle raw bytes
        image_data = base64.b64encode(image_input).decode('utf-8')
    else:
        raise TypeError("Unsupported type for image_input. Expected str, Path, BytesIO, BufferedReader, or bytes.")

    return f"data:{mime};base64,{image_data}"

# Example usage:
# content, info = get_file_data("https://example.com/image.png")
# data_url = prepare_image_for_open_ai(content)
# print(data_url)

# content, info = get_file_data("tmp.png")
# # print(get_file_data('tmp.png'))
# idd =  prepare_image_for_open_ai(content)
# # print(idd)

# content, info = get_file_data("tmp.png")
# print(ac3)

# desc1, info1 = ac3.call_image_text(ready_img_url=idd, img_name='tmp.png')


# print(json.dumps(desc1))
# print (desc1, info1)


idd =  ac2.prepare_image_for_open_ai('tmp.jpg', mime='image/jpeg')

desc2, info2 = ac3.call_image_text(ready_img_url=idd, img_name='tmp.jpg')


print(json.dumps(desc2))
print (desc2, info2)
