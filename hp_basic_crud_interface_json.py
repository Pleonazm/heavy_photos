from dataclasses import dataclass, field
import json
from pathlib import Path
from functools import wraps


from hp_basic_crud_interface import BasicCRUDInterface



@dataclass
class BasicCRUDInterfaceJSON (BasicCRUDInterface):
    """CRUD interface for JSON. All parsed JSON files have to be a list of dictionaries. One dictionary is one object/row
    
    """
    
    uri: str|Path
    name: str = None
    full_data:list = field(default_factory=list)
    not_saved:bool = True


    def require_uri(method):
        """Decorator that checks URI before executing the decorated method."""
        @wraps(method)
        def wrapper(self, *args, **kwargs):

            if not hasattr(self, 'uri'):
                raise AttributeError("Missing 'uri' attribute")
            if not self.uri:
                raise ValueError(
                    f"Cannot execute {method.__name__} - No URI set for {self.__name__}"
                                )
            # Execute the original method
            result = method(self, *args, **kwargs)
            
            return result  # Return the original method's result
        return wrapper

    def __post_init__(self):
        self.uri = Path(self.uri)

    @require_uri
    def _load(self):
        if self.uri.exists():

            read_txt = self.uri.read_text(encoding='utf-8')
            self.full_data = json.loads(read_txt)

    @require_uri
    def _save(self):
        if self.not_saved:
            write_txt = json.dumps(self.full_data)
            # self.uri.write_text(write_txt, encoding='utf-8')
            with self.uri.open("w", encoding="utf-8") as f:
                f.write(write_txt)
        else:
            print('Nothing to save...')


    @require_uri
    def make(self, uri=None, name=None):
        self.uri.parent.mkdir(parents=True, exist_ok=True)
        if uri:
            self.uri = Path(uri)  # Ensure it's a Path object
        if self.uri.exists():
            self._load()
        else:
            self.uri.touch(exist_ok=True)
            self.full_data = []  # Ensure it's an empty list, not `None`
            self._save()

    @require_uri
    def unmake(self) -> bool:
        try:
            self.uri.unlink()
            return True
        except FileNotFoundError:
            print("File not found. Nothing to remove.")
            return False
    @require_uri
    def remake(self, data=None, forced:bool=False):
        if not data:
            data = self.full_data
        json_dump = json.dumps(data)
        if forced or self.not_saved:
            self._save() #self.uri.write_text(data=json_dump, encoding='utf-8')
        else:
            print('No need to save, or not forced')
        self.not_saved = False

    def add(self, data: dict) -> None:
        self.full_data.append(data)
        self.not_saved = True

    def get(self, fields_dict: dict) -> list:
        if not fields_dict:
            return []
        found_sets = [set(obj for obj in self.full_data if obj.get(field) == value) 
                    for field, value in fields_dict.items()]
        if found_sets:
            return list(set.intersection(*found_sets))
        else:
            return []


    def get_all(self):
        if not self.full_data:
            self._load(self.uri)

        return self.full_data

            


    def find(self, find_str:str) -> list:

        # find_list = [obj for obj in self.full_data if find_str in obj['description']]
        find_list = [obj for obj in self.full_data if "description" in obj and find_str in obj["description"]]


        return find_list

    def update(self, data: dict) -> dict:
        for idx, item in enumerate(self.full_data):
            if str(item.get('id')) == str(data.get('id')):
                self.full_data[idx] = {**item, **data}
                self.not_saved = True
                return self.full_data[idx]
        raise ValueError("Item not found")  
 
    def delete(self, id: str):#Temporary Implementation
       initial_length = len(self.full_data)
       self.full_data = [item for item in self.full_data 
                       if str(item.get('id')) != str(id)]
       
       if len(self.full_data) == initial_length:
           raise ValueError("ID not found")
       self.not_saved = True

    def delete_all(self):
        self.full_data = {}
        self._save()

