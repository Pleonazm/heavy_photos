from dataclasses import dataclass, field
import instructor
from openai import OpenAI
from dotenv import dotenv_values
from pprint import pprint
from functools import wraps
from io import BytesIO, BufferedReader
import requests
from pathlib import Path

from pydantic import BaseModel

import base64
import json

from typing import Any

# from typing import Union
# from typing import Union, Tuple



@dataclass
class AI_Client_Call_Wrapper():

    base_url: str = None
    api_key:str = None
    ai_client: OpenAI = None
    # instruct:dict = field(default_factory=lambda:{'model':'gpt-4o-mini', 'response_model': None })
    configs:dict[dict] = field(default_factory=lambda:
                         {'text_text': {'model': 'gpt-4o-mini'},
                          'text_image': {'model': 'dall-e-2'},
                          'text_embeddings': {'model': 'text-embedding-3-small', 'dimensions': 1536},
                          'image_text': {'model':'gpt-4o-mini'},
                          #{'model': 'gpt-4-vision-preview'}#{'model':'gpt-4o-mini'}
                          })
    
    @classmethod    
    def make_from_key(cls, api_key:str):
        """Shortcut"""
        ai_client = OpenAI(api_key=api_key)
        return cls(api_key=api_key, ai_client=ai_client)
    
    @classmethod
    def make_instructor(cls, api_key:str,ai_model:str='gpt-4o-mini', response_model=None):
        """Create directly with Instructor,not OPenAI client"""
        ai_client = instructor.from_openai(OpenAI(api_key=api_key))
        return cls(api_key=api_key, ai_client=ai_client)
        # return cls(api_key=api_key, ai_client=ai_client, instruct={'model': ai_model, 'response_model': response_model})
        
    def change_into_instructor(self, response_model)-> None:
        #Not Working
        self.ai_client = instructor.from_openai(self.ai_client)
        # self.instruct['response_model'] = response_model

    def get_file_data(self, url: str | Path) -> tuple[BufferedReader|bytes, str]: #Rewrite to only get raw data from Storage Objects?
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

    # def prepare_image_for_open_ai(self, image_input: Union[str, Path, BytesIO, BufferedReader, bytes], mime: str = 'image/png') -> str:
    def prepare_image_for_open_ai(self, image_input: str | Path | BytesIO | BufferedReader | bytes, mime: str = 'image/png') -> str:
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
            raise TypeError(f"Unsupported {type(image_input)} type for image_input. Expected str, Path, BytesIO, BufferedReader, or bytes.")

        return f"data:{mime};base64,{image_data}"


    
    @staticmethod
    def configs_override(func):
        """
        Decorator that updates self.configs with the provided 'config_override' dictionary.
        Then calls the decorated method with the remaining arguments.
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if 'config_override' in kwargs:
                # Update self.configs with the provided dictionary
                self.configs.update(kwargs.pop('config_override'))
            # Call the decorated method with the remaining arguments
            return func(self, *args, **kwargs)
        return wrapper

    def get_ai_client(self, **kwargs):
        self.ai_client = OpenAI(api_key=self.api_key, base_url=self.base_url, **kwargs)
        info = 'AI Client created'
        return True, info
    

    @configs_override
    def call_text_text(self, user_prompt:str, system_prompt:str=''):
        # if config_override:
        #     self.configs['text_text'].update(config_override)
        print (f'Text text Model {self.configs["text_text"]}')
        raw_res = self.ai_client.chat.completions.create(
                model=self.configs['text_text']['model'],
                temperature=0,
                messages=[{"role": "system", "content": system_prompt},{"role": "user","content": user_prompt,}],)
                # messages=[{"role": "user","content": user_prompt,},],)
        
        result = raw_res.choices[0].message.content
        info = f'Call done for UP: {user_prompt} SP:{system_prompt}'
        return result, info
    

    @configs_override
    def call_text_image(self, image_desriptor:str):
        
        result = f"Image DATA: {image_desriptor}"
        info = 'image created'
        
        return result, info



    @configs_override
    def call_text_embeddings(self, text_to_emb):
        print('text emb')

        raw_result = self.ai_client.embeddings.create(input=[text_to_emb],
                                                      model=self.configs['text_embeddings']['model'],
                                                      dimensions=self.configs['text_embeddings']['dimensions']
                                                      )
        
        result = raw_result.data[0].embedding
        info = f'Embeddings for {text_to_emb}'
        return result, info
    
    # @configs_override
    def call_image_text(self, ready_img_url:str, img_name:str=None, mime:str='image/png'):

        # response = self.ai_client.chat.completions.create(model=self.configs['image_text']['model'],
        #                                               messages=[
        # {"role": "system", "content": "Describe the image in detail."},
        # {"role": "user", "content": [{"type": "image", "image": img_bytes}]}
        #                                                         ],
        #                                                 max_tokens=150)

        # response_dict = 
        response = self.ai_client.chat.completions.create(model=self.configs['image_text']['model'],
        temperature=0,
        messages=[{"role": "user","content": [{"type": "text","text": "Create a detailed description of the picture. What interesting elements you can see?"},
                {"type": "image_url","image_url": {
                        'url': ready_img_url,#"url": prepare_image_for_open_ai("dall_e_3__sitting_cat.png"),
                        "detail": "high"
                                                    },
                },
                                            ],}],)
        result = response.choices[0].message.content
        info = f'Image Text for image {img_name}'
        return result, info
 
        
    def call_image_text2(self, ready_img_url:str, user_prompt:str, system_prompt:str, img_name:str=None, mime:str='image/png', response_model=None) -> str | Any:

        # response = self.ai_client.chat.completions.create(model=self.configs['image_text']['model'],
        #                                               messages=[
        # {"role": "system", "content": "Describe the image in detail."},
        # {"role": "user", "content": [{"type": "image", "image": img_bytes}]}
        #                                                         ],
        #                                                 max_tokens=150)

        response_dict = {'model':self.configs['image_text']['model'], 'temperature':0,
                         'messages': [{"role": "system", "content": system_prompt},
                             {"role": "user","content": [{"type": "text","text": user_prompt},
                                                         {"type": "image_url","image_url": {'url': ready_img_url,"detail": "high"}},],
                                                         }]}
        if response_model:
            response_dict.update({'response_model':response_model})

        response = self.ai_client.chat.completions.create(**response_dict)

        if response_model:
            result = response
        else:
            result = response.choices[0].message.content
        info = f'Image Text for image {img_name}'
        return result, info
    
    def check_text_image_prompt(user_prompt:str=None, system_prompt:str=None):
        prompts = {}
        default_system_prompt = 'You are experiecnced artist, and have skills in image analysis'
        default_user_prompt = "Create a detailed description of the picture. What interesting elements you can see?"
        if user_prompt is None:
            prompts['user'] = default_user_prompt
            prompts['system'] = default_system_prompt
        return prompts
 

    
if __name__ == "__main__":

    #Temporary quick and dirty testintg, TODO: Write proper tests

    env = dotenv_values(".env")
    ac = AI_Client_Call_Wrapper(api_key=env["OPENAI_API_KEY"])
    # ac.configs['text_text']['model'] = 'gp5'
    ac.get_ai_client()
    # pprint(ac.call_text_embeddings())
    pprint(ac)

    # pprint(ac.call_text_text('How many limbs a centipede has?', 'You are experienced zoologist answer clearly and concise'))#OK
    # pprint(ac.call_text_embeddings('hello world'))#OK
    # ig = [['tmp.jpg', 'image/jpeg'], ['tmp.png', 'image/png']]

    # ready_urls = []

    # for i in ig:
    #     idata, info = ac.get_file_data(i[0])
    #     iprep = ac.prepare_image_for_open_ai(idata, i[1])
    #     ready_urls.append([iprep, i[0]])

    # print(ready_urls)


    ac2 = AI_Client_Call_Wrapper.make_from_key(api_key=env["OPENAI_API_KEY"])

    ac3 = AI_Client_Call_Wrapper.make_instructor(api_key=env["OPENAI_API_KEY"])


    pprint(ac2)
    pprint(ac3)

    tst = 'The image displays a network topology diagram created using GNS3 software.'
    emb, info = ac3.call_text_embeddings(tst)
    pprint(emb[::10])

    # dump_dic = []

    # with open('urls.json', mode='w', encoding='UTF-8') as f:
    #     f.write(json.dumps(ready_urls))

    # for u in ready_urls:
    #     res, inf = ac.call_image_text(u[0])
    #     print(res, inf)
    #     dump_dic.append([res, u[1]])

    # with open('json_dumps.json', mode='a', encoding='UTF-8') as f:
    #     f.write(json.dumps(dump_dic))   

    # pprint(ac.configs)
    # pprint(ac2.configs)

    class UserInfo(BaseModel):
        name: str
        age: int

    # aci = AI_Client_Call_Wrapper.make_instructor(api_key=env["OPENAI_API_KEY"], response_model=UserInfo)
    # print(aci)
    # ac2.change_into_instructor(response_model=UserInfo)
    # print(ac2)









