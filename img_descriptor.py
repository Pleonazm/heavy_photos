from ai_client_wrapper import AI_Client_Call_Wrapper
from hp_storage import Storage
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import dotenv_values
from pprint import pprint
from pydantic import BaseModel

import hashlib


@dataclass
class ImgDescriptor:

    img_storage:Storage = None
    ai_wrapper:AI_Client_Call_Wrapper = None
    img_path:str|Path = None
    img_id: str = None
    mime:str = 'image/jpeg'
    description:str = ''
    embeddings = None




    def get_image_description(self):

        class ImgModel(BaseModel):
            description: str
            metatags: list

        img_description_url = self.ai_wrapper.prepare_image_for_open_ai(image_input=self.img_storage.raw_data,mime=self.mime)
        user_prompt = "Stwórz opis dokładny obrazka, jakie widzisz tam elementy? Wybierz minimum 5 słów które mogą być użyte jako metatagi"
        system_prompt = "Jesteś grafikiem z 10 doświadczeniem"
        result, info = self.ai_wrapper.call_image_text2(ready_img_url=img_description_url, user_prompt=user_prompt, system_prompt=system_prompt, response_model=ImgModel)

        self.description = result.description

        return result
    
    def get_embeddings_from_description(self):
        embeddings, info = self.ai_wrapper.call_text_embeddings(self.description)
        self.embeddings = embeddings
        return embeddings, info
    




if __name__ == '__main__':
    env = dotenv_values(".env")

    st = Storage(load_method='file', save_method='file')

    imd = ImgDescriptor(img_storage=st, mime='image/jpeg', ai_wrapper=AI_Client_Call_Wrapper.make_instructor(api_key=env["OPENAI_API_KEY"]))
    imd.img_storage.load('tmp_st3.jpg')
    imd.img_storage.save('tmp_id.jpg')



    pprint(imd.get_image_description())
    pprint('1111111111111111111111111111111111')
    pprint(imd.get_embeddings_from_description())

    pprint(imd)









    
