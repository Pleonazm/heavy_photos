from hp_storage import DataStoragePhysical
from img_descriptor import ImgDescriptor
from ai_client_wrapper import AI_Client_Call_Wrapper

import json
from dataclasses import dataclass, field
import base64

from benedict import benedict
from pprint import pprint

@dataclass
class HPController():

    ai_wrapper: AI_Client_Call_Wrapper = None
    objects_list: list[ImgDescriptor] = field(default_factory=list)


    def create_full_dump(self):
        """
        Makes full flat dump of all objets
        Use for testing

        :return: List with serialized data
        """
        dump_list = []
        for obj in self.objects_list:
            obj_dict = {}
            obj_dict['id'] = obj.id
            obj_dict['hash'] = obj.img_storage.hash
            obj_dict['raw_data'] =  base64.b64encode(obj.img_storage.raw_data).decode("utf-8")
            obj_dict['load_method'] = obj.img_storage.load_method
            obj_dict['uri'] = obj.img_storage.uri
            obj_dict['tags'] = obj.tags
            obj_dict['mime'] = obj.mime
            obj_dict['description'] = obj.description
            obj_dict['embeddings'] = obj.embeddings
            dump_list.append(obj_dict)
        return dump_list
    
    def load_full_dump(self, dump_load_list:list):
        """
        Loads data from provided list, deserializes then manually creates objects
        
        :param dump_load_list: List with serialized data
        """
        for obj_dict in dump_load_list:
            new_obj = ImgDescriptor()
            new_obj.img_storage = DataStoragePhysical()
            
            new_obj.id = obj_dict['id']
            new_obj.img_storage.hash = obj_dict['hash']
            new_obj.img_storage.raw_data = base64.b64decode(obj_dict['raw_data'])
            new_obj.img_storage.load_method = obj_dict['load_method']
            new_obj.img_storage.uri = obj_dict['uri']
            new_obj.tags = obj_dict['tags'] 
            new_obj.mime = obj_dict['mime'] 
            new_obj.description = obj_dict['description']
            new_obj.embeddings = obj_dict['embeddings']
            self.objects_list.append(new_obj)



##########

if __name__ == "__main__":
    
    # c = HPController()
    # test_data = [{"id": "3b42e886e2651bd70047b2131762ed646052fa33efdea12579c70011e76026c4", "uri": "example_data/dino.png", "load_method": "file"},
                
    #             {"id": "c3545bf0088c0e993f74e4fbe3000dc68660819006ab91187f2a36c1caa81211", "uri": "example_data/monk.jpg", "load_method": "file"}]

    # dino_det = benedict("example_data/3b42e886e2651bd70047b2131762ed646052fa33efdea12579c70011e76026c4.json", format='json')
    # monk_det = benedict('example_data/c3545bf0088c0e993f74e4fbe3000dc68660819006ab91187f2a36c1caa81211.json', format='json')

    # ds = DataStoragePhysical(load_method='file', uri='example_data/dino.png')
    # ms = DataStoragePhysical(load_method='file', uri='example_data/monk.jpg')

    # # idd = ImgDescriptor()

    # c.objects_list = [
    #     ImgDescriptor(embeddings=dino_det['embeddings'],id=dino_det['id'], mime=dino_det['mime'], description=dino_det['description'], tags=dino_det['tags'],img_storage=ds),
    #     ImgDescriptor(embeddings=monk_det['embeddings'],id=monk_det['id'], mime=monk_det['mime'], description=monk_det['description'], tags=monk_det['tags'],img_storage=ms)
                   
    #     ]

    # for o in c.objects_list:
    #     o.img_storage.load()

    # fd = c.create_full_dump()

    # with open("example_data/full_dump.json", "w") as f:
    #     json.dump(fd, f, indent=4)

    # c2 = HPController()
    # c2.load_full_dump(fd)

    pprint('END')


