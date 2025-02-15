from dataclasses import dataclass, field
from openai import OpenAI
from dotenv import dotenv_values
from pprint import pprint
from functools import wraps
from io import BytesIO
import requests

import base64
from pathlib import Path
from io import BytesIO
from typing import Union


@dataclass
class AI_Client_Call_Wrapper():

    base_url: str = None
    api_key:str = None
    ai_client: OpenAI = None
    configs:dict = field(default_factory=lambda:
                         {'text_text': {'model': 'gpt-4o-mini'},
                          'text_image': {'model': 'dall-e-2'},
                          'text_embeddings': {'model': 'text-embedding-3-small', 'dim': 1536},
                          'image_text': {'model':'gpt-4o-mini'}
                          })
    
    @classmethod
    """Shortcut"""
    def make_from_key(cls, api_key):
        ai_client = OpenAI(api_key=api_key)
        return cls(api_key=api_key, ai_client=ai_client)
    

    def get_file_data(url:str|Path):

        content = None
        info = None

        if Path(url).is_file:

            # content = {'content': Path.open(url), 'type': url.suffix[1::]}
            content = Path.open(url)
            info = f'local file {url}'

        elif isinstance(url, str):
            content = requests.get(url).content
            info = f"remote file {url}"

        else:
            content = None
            info = f'Wrong url: {url}'

        return content, info





    def prepare_image_for_open_ai(image_input: Union[str, Path, BytesIO], mime: str = 'image/png') -> str:
        """
        Prepares an image for OpenAI by encoding it as a base64 data URL.

        Args:
            image_input (Union[str, Path, BytesIO]): The image input, which can be a file path (str or Path) or a BytesIO object.
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
        else:
            raise TypeError("Unsupported type for image_input. Expected str, Path, or BytesIO.")

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
        
        result = f"IMage DATA: {image_desriptor}"
        info = 'image created'
        
        return info, result



    @configs_override
    def call_text_embeddings(self, text_to_emb):
        print('text emb')

        raw_result = self.ai_client.embeddings.create(input=[text_to_emb],
                                                      model=self.configs['text_embeddings']['model'],
                                                      )
        
        result = raw_result.data[0].embedding
        info = f'Embeddings for {text_to_emb}'
        return result, info
 

    
if __name__ == "__main__":

    env = dotenv_values(".env")
    ac = AI_Client_Call_Wrapper(api_key=env["OPENAI_API_KEY"])
    # ac.configs['text_text']['model'] = 'gp5'
    ac.get_ai_client()
    # pprint(ac.call_text_embeddings())
    pprint(ac)

    # pprint(ac.call_text_text('ile nóg ma stonoga', 'jesteś doświadcznoym zoologiem odpowiadaj jasno'))#OK
    # pprint(ac.call_text_embeddings('hello world'))#OK
    ac.call_text_image('zzzz', config_override={'text2': 'new_text'})

    ac2 = AI_Client_Call_Wrapper.make_from_key(api_key=env["OPENAI_API_KEY"])

    pprint(ac2)

    pprint(ac.configs)
    pprint(ac2.configs)







