
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import dotenv_values
from pprint import pprint
from pydantic import BaseModel
from functools import wraps

import json
import copy


import hashlib

from ai_client_wrapper import AI_Client_Call_Wrapper
# from hp_storage import Storage
from hp_storage import DataStoragePhysical



@dataclass
class ImgDescriptor:

    img_storage:DataStoragePhysical = None
    ai_wrapper:AI_Client_Call_Wrapper = None
    img_path:str|Path = None
    id:str = None
    mime:str = 'image/jpeg'
    description:str = ''
    embeddings:object = None
    tags: list[str] = field(default_factory=list)

    def _enforce_proper_mime(method):
        """Decorator to ensure self.mime is set before method execution.
        
        - Uses self.img_storage.guess_mime_type() if self.mime is missing.
        - Raises ValueError if MIME type cannot be determined.
        """
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            # Check if mime is already valid
            if not self.mime:
                # Attempt to guess from img_storage
                if self.img_storage:
                    raise AttributeError("No Storage Present")
                    
                guessed_mime = self.img_storage.get_mime_type()
                if not guessed_mime:
                    raise ValueError("MIME type could not be determined")
                    
                self.mime = guessed_mime  # Set validated mime
            
            # Execute the decorated method with guaranteed self.mime
            return method(self, *args, **kwargs)
        
        return wrapper
    
    def get_mime(self):
        if self.mime:
            return self.mime
        else:
            return self.img_storage.get_mime_type()




    def get_image_description(self, external_ai=None):

        class ImgModel(BaseModel):
            description: str
            tags: list

        ai_used = None

        if external_ai:
            ai_used = external_ai
        else:
            ai_used = self.ai_wrapper


        # img_description_url = self.ai_wrapper.prepare_image_for_open_ai(image_input=self.img_storage.raw_data,mime=self.mime)
        img_description_url = ai_used.prepare_image_for_open_ai(image_input=self.img_storage.raw_data,mime=self.mime)
        user_prompt = "Describe this picture in detail. Select 10 words which could be used as good metatags for this picture. Use included response model"
        system_prompt = "You are an artist, with the good eye for detail and 10 years of experience"
        result, info = self.ai_wrapper.call_image_text2(ready_img_url=img_description_url, user_prompt=user_prompt, system_prompt=system_prompt, response_model=ImgModel)

        self.description = result.description
        self.tags = result.tags

        return result
    
    def get_image_description2(self, resp_model, external_ai=None):#Tmp variant, to test things

        ai_used = None

        if external_ai:
            ai_used = external_ai
        else:
            ai_used = self.ai_wrapper


        # ai_used.change_into_instructor(resp_model)
        # img_description_url = self.ai_wrapper.prepare_image_for_open_ai(image_input=self.img_storage.raw_data,mime=self.mime)
        img_description_url = ai_used.prepare_image_for_open_ai(image_input=self.img_storage.raw_data,mime=self.mime)
        user_prompt = "Describe this picture in detail. Select 10 words which could be use as good metatags for this picture. Use included response model"
        system_prompt = "You are an artist, with the good eye to detail and 10 years of experience"
        result, info = self.ai_wrapper.call_image_text2(ready_img_url=img_description_url,
                                                        user_prompt=user_prompt, system_prompt=system_prompt,
                                                        response_model=resp_model)
        
        self.description = result.description
        self.tags = result.tags

        return result

    
    def get_embeddings_from_description(self) -> tuple[list, str]:
        embeddings, info = self.ai_wrapper.call_text_embeddings(self.description)
        self.embeddings = embeddings
        return embeddings, info
    
    def get_as_dict(self) -> dict:
        result_dict = {'id': self.img_storage.hash,
                       'mime': self.get_mime(),
                       'description': self.description,
                       'tags': self.tags,
                       'embeddings': self.embeddings,
                       'uri': self.img_storage.uri
                       }
        return result_dict
    
    def get_index_data(self) -> dict:
        result_dict = {'id': str(self.img_storage.hash),
                       'uri': str(self.img_storage.uri),
                       'load_method': self.img_storage.load_method}
        return result_dict
    
    def load_img_data(self) -> None:
        self.img_storage.load()
        self.id = self.img_storage.hash

    def dump(self, flatten=True, no_raw_data=False) -> dict:
        """Dumps data into a serializable dictionary"""
        if not self.id:
            raise ValueError('No ID present')
        dump_dict = copy.deepcopy(self.__dict__)
        dump_storage = self.img_storage.dump(no_raw_data=no_raw_data)
        del dump_dict['img_storage']
        del dump_dict['ai_wrapper']
        if flatten:
            dump_dict.update(dump_storage)
        else:
            dump_dict.update({'storage': dump_storage})

        return dump_dict


    




if __name__ == '__main__':
    env = dotenv_values(".env")

    # i = DataStoragePhysical(uri='ssss', raw_data=b"1234567899567432232798763423467", load_method='FILE') 
    # idd = ImgDescriptor(img_storage=i)

    # d = idd.dump()

    # print(idd)
    # print('--------------------------------')
    # print(d)







    
