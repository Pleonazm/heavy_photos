from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
import requests

class StorageError(Exception):
    """Exception for Storage problems

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


@dataclass
class Storage():
    raw_data: bytes = None
    save_method:str = ''
    load_method:str = ''
    configs:dict[dict] = field(default_factory=dict)

    def configure_s3(self, aws_access_key_id, aws_secret_access_key, aws_endpoint_url_s3):
        self.configs['aws_s3']['aws_access_key_id'] = aws_access_key_id
        self.configs['aws_s3']['aws_secret_access_key'] = aws_secret_access_key
        self.configs['aws_s3']['aws_endpoint_url_s3'] = aws_endpoint_url_s3

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
        #use AWS SDK to connect, using self.configs
        pass


    def save(self, *args, **kwargs):
        save_functions = {'file': self.save_file, 'http_post': self.save_http_post, 'aws_s3': self.save_aws_s3}
              
        if self.save_method in save_functions:
            save_functions[self.save_method](*args, **kwargs)
        else:
            raise StorageError('Wrong Save Function')

    def load_http_get(self,url):
        resp = requests.get(url=url)
        resp.raise_for_status()
        self.raw_data = resp.content
        # if resp.status_code == 404:
        #     raise StorageError('No resource found')
        # else:
        #     self.raw_data = resp.content


    def load_file(self, load_path):
        load_path = Path(load_path)
        with open(load_path, mode='rb') as f:
            self.raw_data = f.read()

    def load_aws_s3(self):
        #use AWS SDK to connect, using self.configs
        pass



    def load(self, *args, **kwargs):
        load_functions = {'file': self.load_file, 'http_get': self.load_http_get, 'aws_s3': self.load_aws_s3}
        
        if self.load_method in load_functions:
            load_functions[self.load_method](*args, **kwargs)
        else:
            raise StorageError('Wrong Load Function')  