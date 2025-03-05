
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import dotenv_values
from pprint import pprint
from pydantic import BaseModel
import json

import hashlib

from ai_client_wrapper import AI_Client_Call_Wrapper
# from hp_storage import Storage
from hp_storage import DataStoragePhysical
from hp_data_link import JSONDataLink



@dataclass
class ImgDescriptor:

    img_storage:DataStoragePhysical = None
    ai_wrapper:AI_Client_Call_Wrapper = None
    img_path:str|Path = None
    id: str = None
    mime:str = 'image/jpeg'
    description:str = ''
    embeddings = None
    tags: list = field(default_factory=list)




    def get_image_description(self):

        class ImgModel(BaseModel):
            description: str
            tags: list

        img_description_url = self.ai_wrapper.prepare_image_for_open_ai(image_input=self.img_storage.raw_data,mime=self.mime)
        user_prompt = "Stwórz opis dokładny obrazka, jakie widzisz tam elementy? Wybierz minimum 5 słów które mogą być użyte jako metatagi"
        system_prompt = "Jesteś grafikiem z 10 doświadczeniem"
        result, info = self.ai_wrapper.call_image_text2(ready_img_url=img_description_url, user_prompt=user_prompt, system_prompt=system_prompt, response_model=ImgModel)

        self.description = result.description
        self.tags = result.tags

        return result
    
    def get_image_description2(self, resp_model):#Tmp variant, to test things
        # self.ai_wrapper.change_into_instructor(resp_model)
        img_description_url = self.ai_wrapper.prepare_image_for_open_ai(image_input=self.img_storage.raw_data,mime=self.mime)
        user_prompt = "Describe this picture in detail. Select 10 words which could be use as good metatags for this picture. Use included response model"
        system_prompt = "You are an artist, with good eye to detail and 10 years of experience"
        result, info = self.ai_wrapper.call_image_text2(ready_img_url=img_description_url,
                                                        user_prompt=user_prompt, system_prompt=system_prompt,
                                                        response_model=resp_model)
        
        self.description = result.description
        self.tags = result.tags

        return result

    
    def get_embeddings_from_description(self):
        embeddings, info = self.ai_wrapper.call_text_embeddings(self.description)
        self.embeddings = embeddings
        return embeddings, info
    
    def get_data_as_dict(self):
        result_dict = {'id': self.img_storage.hash,
                       'mime': self.mime,
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
    
    def load_img_data(self):
        self.img_storage.load()
        self.id = self.img_storage.hash

    




if __name__ == '__main__':
    env = dotenv_values(".env")

    st = DataStoragePhysical(load_method='file', save_method='file')

    imd = ImgDescriptor(img_storage=st, mime='image/jpeg', ai_wrapper=AI_Client_Call_Wrapper.make_instructor(api_key=env["OPENAI_API_KEY"]))
    imd.img_storage.load('tmp_st3.jpg')
    imd.img_storage.save('tmp_id.jpg')



    pprint(imd.get_image_description())
    pprint('1111111111111111111111111111111111')
    pprint(imd.get_embeddings_from_description())

    # pprint(imd)
    dd = {'embeddings': imd.description,
          'id': imd.img_storage.hash,
          'uri': imd.img_storage.uri,
          'embeddings': imd.embeddings,
          'description': imd.description,
          'tags': imd.tags
    }


    # dd = {'embeddings': 'imd.description',
    #       'id': 'imd.img_id',
    #       'uri': 'imd.img_storage.hash',
    #       'embeddings': 'imd.embeddings',
    #       'description': 'imd.description' }

    jd = JSONDataLink(file_path=Path('example/test.json'))
    pprint(jd)
    res_d = imd.get_data_as_dict()
    jd.write_data(dd)









    
