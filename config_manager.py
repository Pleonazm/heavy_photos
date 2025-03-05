from dataclasses import dataclass
from qdrant_client import QdrantClient
from pathlib import Path
from dotenv import dotenv_values


@dataclass
class Config_Manager:
    ai_api_key:str = None
    qdrant_url:str = "http://localhost:6333" #":memory:"
    storage_path:Path|str = ''

    def get_qdrant_client(self):
        qdrant = QdrantClient(self.qdrant_url)
        return qdrant

    def get_ai_wrapper(self):
        ai_wrapper = {'key': self.ai_api_key, 'from_key': 'wrapper_fromkey'}
        return ai_wrapper
    
    def from_dotenv(self, env_path:str='.env'):
        env = dotenv_values(env_path)
        for e_name, e_val in env:
            self.__setattr__(e_name,e_val)

    def get_config_as_json(config_data: dict=None) -> io.BytesIO:
        """
        Serializes a dictionary into a BytesIO object.
        
        Args:
            d (dict): The dictionary to serialize.
        
        Returns:
            io.BytesIO: A byte stream containing the serialized dictionary.
        """
        config_data = {'main':{'ai_api_key': self.ai_api_key}, 'embeddings':{'qdrant_url': self.qdrant_url}}
        json_str = json.dumps(config_data, indent=4, sort_keys=True)
        byte_stream = io.BytesIO(json_str.encode('utf-8'))
        return byte_stream








    