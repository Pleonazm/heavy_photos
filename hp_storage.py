from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from functools import wraps
import json
import base64
import copy
import mimetypes
import filetype
from urllib.parse import urlparse

import requests
import hashlib



from hp_basic_crud_interface import BasicCRUDInterface

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
    mime:str = None


    def _to_bytes(self) -> bytes:
        """Convert raw_data to first 2048 bytes (handles bytes/BytesIO/files)"""
        try:
            if isinstance(self.raw_data, bytes):
                return self.raw_data[:2048]
            if isinstance(self.raw_data, BytesIO):
                return self.raw_data.getvalue()[:2048]
            if hasattr(self.raw_data, 'read'):
                pos = self.raw_data.tell()
                self.raw_data.seek(0)
                data = self.raw_data.read(2048)
                self.raw_data.seek(pos)
                return data
            return b''
        except Exception:
            return b''

    def _extract_filename(self) -> str | None:
        """Extract filename from URI (supports Path/str/URLs)"""
        try:
            uri = str(self.uri)
            if '://' in uri:
                path = urlparse(uri).path
            else:
                path = uri
            return Path(path).name if path else None
        except Exception:
            return None


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
    


    def get_mime_type(self):
        """Method to detect MIME type using class helpers"""

        if self.mime:
            return self.mime
        
        
        # 1. Content-based detection
        buffer = self._to_bytes()
        mime = None
        if buffer:
            kind = filetype.guess(buffer)
            mime = kind.mime if kind else None
        
        # 2. Filename fallback
        if not mime:
            filename = self._extract_filename()
            if filename:
                mime, _ = mimetypes.guess_type(filename)

        
        self.mime = mime
        return self.mime



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
            self.uri = uri

        resp = requests.get(url=self.uri)
        resp.raise_for_status()
        self.raw_data = resp.content
        self.get_mime_type()
        # if resp.status_code == 404:
        #     raise StorageError('No resource found')
        # else:
        #     self.raw_data = resp.content


    @compute_hash
    def load_file(self, load_path:str|Path=None):
        if load_path:
            # load_path = Path(load_path)
            self.uri = Path(load_path)
        # else:
        load_path = Path(self.uri)
        with open(load_path, mode='rb') as f:
            self.raw_data = f.read()
        self.get_mime_type()


    @compute_hash
    def load_raw(self,raw_data:bytes):
        self.raw_data = raw_data
        self.get_mime_type()



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
        self.get_mime_type()
        
    def dump(self) -> dict:
        """Dumps data into a serializable dictionary"""
        dump_dict = copy.deepcopy(self.__dict__)
        dump_dict['raw_data'] = base64.b64encode(self.raw_data).decode("utf-8")
        return dump_dict
        


        
@dataclass
class MetaDataStorage:

    id: str = None
    description: str = None
    uri: str|Path = None
    tags: list[str] = field(default_factory=list)

    def get_as_dict(self):
        return self.__dict__



@dataclass
class ObjectIndex:

    full_data: list = None # {id/hash:'', load_method:'', uri:''}
    data_link: BasicCRUDInterface = None#DataLink

class IndexLoader(ABC):
    @abstractmethod
    def load_data(self):
        """Load data from a source."""
        pass

if __name__ == '__main__':
    pass

    # #Temporary quick/dirty test, do proper testing later

    ds1 = DataStoragePhysical(uri='test_data/monk.jpg',load_method='local')
    ds1.load_file()
    ds2 = DataStoragePhysical(uri='test_data/monk.png', raw_data=b"123456", load_method='local')
    ds3 = DataStoragePhysical(uri='test_data/dino.png', raw_data=b"123456", load_method='local')
    ds3.load_file()
    d1 = ds1.dump()
    d2 = ds2.dump()

    # print(ds1)
    # print('--')
    # print(d1)
    # print('--')
    # print(ds2)
    # print('--')
    # print(d2)

    # print(ds1.guess_mime_type())
    # print(ds1.mime)
    print(ds1.mime)
    print(ds2.mime)
    print(ds3.mime)