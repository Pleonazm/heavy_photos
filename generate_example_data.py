import http.server
from dotenv import load_dotenv, dotenv_values
from pprint import pprint
from pathlib import Path
import json

from benedict import benedict
from pydantic import BaseModel

from hp_storage import DataStoragePhysical
from ai_client_wrapper import AI_Client_Call_Wrapper
from img_descriptor import ImgDescriptor
from hp_data_link import JSONDataLink
from hp_controller import HPController


# import requests

# Configure data
load_dotenv()
env = dotenv_values('.env')
img_list_local = [{'uri': Path('example_data/dino.png'), 'mime': 'image/png'},
            {'uri': Path('example_data/monk.jpg'), 'mime': 'image/jpeg'}
            ]

img_list_remote = [{'uri': 'http://localhost:9000/dino.png', 'mime': 'image/png'},
            {'uri': 'http://localhost:9000/monk.jpg', 'mime': 'image/jpeg'}
            ]

class ImgInfoModel(BaseModel):
    description: str
    tags: list[str]


# LowLevel: Create StorageObjects with Images: [storage_obj, mime]

s_obs = [[DataStoragePhysical(load_method='file',uri=i['uri']),i['mime']] for i in img_list_local]
for so in s_obs:
    so[0].load()

# LowLevel: Create AI Wrapper

ac = AI_Client_Call_Wrapper.make_from_key(api_key=env["OPENAI_API_KEY"])

# LowLewel: Create URL for image_text prompts (not needed usually)

ready_urls = []
ready_urls = [ac.prepare_image_for_open_ai(s[0].raw_data,mime=s[1]) for s in s_obs]

# Normal: Image Descriptor, create test tables

i_desc_local = [ImgDescriptor(img_path=i['uri'], 
                        ai_wrapper=AI_Client_Call_Wrapper.make_instructor(api_key=env["OPENAI_API_KEY"],response_model=ImgInfoModel),
                        mime=i['mime'],
                        img_storage=DataStoragePhysical(load_method='file',uri=i['uri'])
                        )
                        for i in img_list_local
                        ]
i_desc_remote = [ImgDescriptor(img_path=i['uri'], 
                        ai_wrapper=AI_Client_Call_Wrapper.make_instructor(api_key=env["OPENAI_API_KEY"], response_model=ImgInfoModel),
                        mime=i['mime'],
                        img_storage=DataStoragePhysical(load_method='http_get',uri=i['uri'])
                        )
                        for i in img_list_remote
                        ]



# storage_index = []

def test_img_desc(i_desc, idx_path="example_data/storage_index.json"):

    storage_index = []

    for idr in i_desc:
        idr.img_storage.load()
        idr.get_image_description2(ImgInfoModel)
        idr.get_embeddings_from_description()
        i_dict = idr.get_data_as_dict()
        st_idx = {'uri':str(idr.img_path), 'hash':idr.img_storage.hash}
        dest = Path(f'example_data/{idr.img_storage.hash}.json')
        jd = JSONDataLink(dest)
        jd.write_data(i_dict)
        storage_index.append(idr.get_index_data())
    # jd_st = JSONDataLink(Path(idx_path))
    # jd_st.write_data(storage_index)
    with open(Path(idx_path), mode='w') as f:
        f.write(json.dumps(storage_index))

if __name__ == '__main__':
    print('START')

    #local
    test_img_desc(i_desc_local, "example_data/storage_index_local_embed.json")
    #remote, needs http server to work
    # test_img_desc(i_desc_remote, "example_data/storage_index_remote.json")



    #Low Level Print No need?

    # # Remove Raw Data for printing
    # for s in s_obs:
    #     s[0].raw_data = None
    # pprint(env['OPENAI_API_KEY'])
    # pprint(ac)
    # pprint(ready_urls)
    # pprint(s_obs)
    # pprint(i_desc)

    # b = benedict(Path('example_data/3b42e886e2651bd70047b2131762ed646052fa33efdea12579c70011e76026c4.png'))
    # b['embeddings'] = None
    # pprint(b)

    # Controller Full Dump test

    c = HPController()
    test_data = [{"id": "3b42e886e2651bd70047b2131762ed646052fa33efdea12579c70011e76026c4", "uri": "example_data/dino.png", "load_method": "file"},
                
                {"id": "c3545bf0088c0e993f74e4fbe3000dc68660819006ab91187f2a36c1caa81211", "uri": "example_data/monk.jpg", "load_method": "file"}]

    dino_det = benedict("example_data/3b42e886e2651bd70047b2131762ed646052fa33efdea12579c70011e76026c4.json", format='json')
    monk_det = benedict('example_data/c3545bf0088c0e993f74e4fbe3000dc68660819006ab91187f2a36c1caa81211.json', format='json')

    ds = DataStoragePhysical(load_method='file', uri='example_data/dino.png')
    ms = DataStoragePhysical(load_method='file', uri='example_data/monk.jpg')

    # idd = ImgDescriptor()

    c.objects_list = [
        ImgDescriptor(embeddings=dino_det['embeddings'],id=dino_det['id'], mime=dino_det['mime'], description=dino_det['description'], tags=dino_det['tags'],img_storage=ds),
        ImgDescriptor(embeddings=monk_det['embeddings'],id=monk_det['id'], mime=monk_det['mime'], description=monk_det['description'], tags=monk_det['tags'],img_storage=ms)
                   
        ]

    for o in c.objects_list:
        o.img_storage.load()

    fd = c.create_full_dump()

    # with open("example_data/full_dump.json", "w") as f:
    #     json.dump(fd, f, indent=4)

    c2 = HPController()
    c2.load_full_dump(fd)