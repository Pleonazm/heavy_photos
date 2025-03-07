from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from functools import wraps
import json

import requests
import hashlib

class StorageError(Exception):
    """Exception for Storage problems

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


@dataclass
class DataStoragePhysical():
    raw_data: bytes = None
    save_method:str = ''
    load_method:str = ''
    configs:dict[dict] = field(default_factory=dict)
    hash:str = None
    uri:str|Path = None

    def configure_s3(self, aws_access_key_id, aws_secret_access_key, aws_endpoint_url_s3):
        self.configs['aws_s3']['aws_access_key_id'] = aws_access_key_id
        self.configs['aws_s3']['aws_secret_access_key'] = aws_secret_access_key
        self.configs['aws_s3']['aws_endpoint_url_s3'] = aws_endpoint_url_s3

    def compute_hash(method):
        """Decorator that computes SHA-256 hash after executing the decorated method."""
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            # Execute the original method
            result = method(self, *args, **kwargs)

            # Compute hash only if self.raw_data is set
            if hasattr(self, 'raw_data'):
            # if hasattr(self, 'raw_data') and isinstance(self.raw_data, bytes):
                self.hash = hashlib.sha256(self.raw_data).hexdigest()
            else:
                raise AttributeError("self.raw_data is not set or is not of type bytes.")
            
            return result  # Return the original method's result
        return wrapper

    def save_file(self, save_path):
        save_path = Path(save_path)
        with open(save_path, mode='wb') as f:
            f.write(self.raw_data)

    def save_http_post(self, url):
        resp = requests.post(url=url,data=self.raw_data)
        resp.raise_for_status()
        if resp.status_code != 200:
            raise StorageError('Remote post error')
        
    def save_aws_s3(self):
        if not self.configs['aws_s3']:
            raise StorageError('No AWS S3 Config')
        #use AWS SDK to connect, using self.configs
        pass


    def save(self, *args, **kwargs):
        save_functions = {'file': self.save_file, 'http_post': self.save_http_post, 'aws_s3': self.save_aws_s3}
              
        if self.save_method in save_functions:
            save_functions[self.save_method](*args, **kwargs)
        else:
            raise StorageError('Wrong Save Function')
    @compute_hash
    def load_http_get(self,uri:str=None):
        if uri:
            resp = requests.get(url=uri)
        else:
            resp = requests.get(url=self.uri)
        resp.raise_for_status()
        self.raw_data = resp.content
        # if resp.status_code == 404:
        #     raise StorageError('No resource found')
        # else:
        #     self.raw_data = resp.content

    @compute_hash
    def load_file(self, load_path:str|Path=None):
        if load_path:
            load_path = Path(load_path)
        else:
            load_path = Path(self.uri)
        with open(load_path, mode='rb') as f:
            self.raw_data = f.read()
    
    @compute_hash
    def load_raw(self,raw_data:bytes):
        self.raw_data = raw_data

    @compute_hash
    def load_aws_s3(self):
        if not self.configs['aws_s3']:
            raise StorageError('No AWS S3 Config')
        #use AWS SDK to connect, using self.configs
        pass



    def load(self, *args, **kwargs):
        load_functions = {'file': self.load_file, 'http_get': self.load_http_get, 'aws_s3': self.load_aws_s3,'raw':self.load_raw}
        
        if self.load_method in load_functions:
            load_functions[self.load_method](*args, **kwargs)
        else:
            raise StorageError('Wrong Load Function')


        
@dataclass
class MetaDataStorage:

    id: str = None
    description: str = None
    uri: str|Path = None
    tags: list[str] = field(default_factory=list)

    def get_as_dict(self):
        return self.__dict__



class BasicCRUDInterface(ABC):

    @abstractmethod
    def make(self) -> None:
        pass
    def remake(self, data=None):
        pass
    @abstractmethod
    def unmake(self) -> bool:
        pass


    def add(self, data:dict) -> None:
        pass
    def get(self, id:str) -> dict:
        pass
    def get_all(self) -> list:
        pass
    def find(self, data:dict) -> dict:
        pass
    def update(self, data:dict) -> dict:
        pass
    def delete(self, id:str):
        pass
    def delete_all(self) -> bool:
        pass


@dataclass
class DataStorageIndexJSON(BasicCRUDInterface):

    uri:str|Path
    full_index_data:list = field(default_factory=list)
    not_saved:bool = True

    def __post_init__(self):
        self.uri = Path(self.uri)

    def _set_uri(self, uri:str|Path):
        self.uri = Path(uri)

    def make(self) -> bool:
        self.uri.touch(self.url, exist_ok=True)
        return True
    
    def add(self, data:dict) -> None:
        self.full_index_data.append(data)
        self.not_saved = True

    def get(self, id:str) -> dict:
        found = [obj for obj in self.full_index_data if obj['id'] in [id]]

        return found[0]


    def get_all(self) -> list:
        # self.full_index_data = self.uri.open(encoding='UTF-8')
        read_txt = self.uri.read_text()
        self.full_index_data = json.loads(read_txt)
        return self.full_index_data

    def find(self, data:dict) -> dict:#only supports one pair for now
        if self.full_index_data:
            pass
        else:
            self.get_all()
        keys = data.keys()
        values = data.values()

        found_list = []

        #temp for one k/v pair
        for field, value in data.items():
            found = [obj for obj in self.full_index_data if obj[field] == value]

        return found
    
    def update(self, id:str, data:dict) -> dict:
        found_obj = self.get(id)
        if found_obj:
            self.full_index_data.remove(found_obj)
            found_obj.update(data)
            self.full_index_data.append(found_obj)
            self.not_saved = True
            return found_obj
        else:
            return {}
    


        pass
    def delete(self,id:str):
        found = self.get(id)
        self.full_index_data.remove(found)
        self.not_saved = True

    def delete_all() -> bool:
        pass
    def remake(self, data=None, forced:bool=False):
        if not data:
            data = self.full_index_data
        json_dump = json.dumps(data)
        if forced or self.not_saved:
            self.uri.write_text(data=json_dump, encoding='utf-8')
        else:
            print('No need to save, or not forced')
        self.not_saved = False
    
    def unmake(self) -> bool:
        # try:
            self.uri.unlink()
            return True
        # except FileNotFoundError:
        #     print("File not found. Nothing to remove.")
        #     return False



@dataclass
class ObjectIndex:

    full_data:list = None # {id/hash:'', load_method:'', uri:''}
    data_link = None #DataLink

class IndexLoader(ABC):
    @abstractmethod
    def load_data(self):
        """Load data from a source."""
        pass
