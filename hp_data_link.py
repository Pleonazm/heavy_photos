from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from benedict import benedict

from pprint import pprint

from hp_storage import DataStorage, MetaDataStorage


# Step 1: Define an abstract base class (interface) for data loaders
class DataLink(ABC):
    @abstractmethod
    def load_data(self):
        """Load data from a source."""
        pass

    def replace_data(self):
       """Replaces data with a new one."""
       pass

    def update_data(self):
        """Updates existing data."""
        pass

    def write_data(self):
        """Exports data."""
        pass

# Step 2: Implement concrete data loaders
@dataclass
class JSONDataLink(DataLink):

    file_path:str = ''

    def load_data(self) -> dict|benedict:
        loaded_data = benedict(self.file_path, format='json')
        return loaded_data['values']
        # with open(self.file_path, "r") as file:
        #     return file.read()

    def replace_data(self, new_data:dict|benedict) -> None:
        self.write_data(new_data)
        # data_to_write = benedict(new_data)
        # data_to_write.to_json(file_path=self.file_path)

    def update_data(self, new_data:dict|benedict) -> None:
        base_data = self.load_data(self.file_path)
        upddated_data = base_data | new_data
        self.write(upddated_data)

    def write_data(self, new_data:dict|benedict) -> None:
        data_to_write = benedict(new_data)
        data_to_write.to_json(file_path=self.file_path)

#placeholder
class DatabaseDataLink(DataLink):
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def load(self):
        # Simulate database loading
        return f"Data from database: {self.connection_string}"
#placeholder
class APIDataLink(DataLink):
    def __init__(self, api_url):
        self.api_url = api_url

    def load(self):
        # Simulate API loading
        return f"Data from API: {self.api_url}"


@dataclass
class DataLoader():

    data_link:DataLink
    # data_storage:list[DataStorage] = field(default_factory=list)
    # metadata_storage:list[MetaDataStorage] = field(default_factory=list)
    data_objects:list[DataStorage|MetaDataStorage] = field(default_factory=list)
    

    def load_data(self, id=None):

        loaded_data = self.data_link.load_data()
        self.data_objects = [self.process_data_item(data_row) for data_row in loaded_data]

        # loaded_data['id'] = loaded_data['hash'] #TMP
        # data = {k:v for k,v in loaded_data.items() if k in ['hash', 'uri']}
        # metadata = {k:v for k,v in loaded_data.items() if k in ['id', 'description', 'tags', 'uri']}
        # if not self.data_storage:
        #     self.data_storage.append(DataStorage(**data))
        # if not self.metadata_storage:
        #     self.metadata_storage.append(MetaDataStorage(**metadata))

    def process_data_item(self, data_item_row:dict):
        data_item_row['id'] = data_item_row['hash']
        data = {k:v for k,v in data_item_row.items() if k in ['hash', 'uri', 'load_method']}
        metadata = {k:v for k,v in data_item_row.items() if k in ['id', 'description', 'tags', 'uri']}
        item_row = {'data': DataStorage(**data), 'metadata': MetaDataStorage(**metadata)}
        return item_row



# Step 3: Client code that uses the data loader, placeholder
class DataProcessor:
    def __init__(self, data_loader: DataLink):
        self.data_loader = data_loader

    def process(self):
        data = self.data_loader.load()
        print(f"Processing data: {data}")

# # Step 4: Usage
# file_loader = FileDataLink("data.txt")
# db_loader = DatabaseDataLink("postgres://user:password@localhost:5432/mydb")
# api_loader = APIDataLink("https://api.example.com/data")

# # Client code doesn't know or care about the specific data loader
# processor = DataProcessor(file_loader)
# processor.process()  # Output: Processing data: <contents of data.txt>

# processor = DataProcessor(db_loader)
# processor.process()  # Output: Processing data: Data from database: postgres://user:password@localhost:5432/mydb

# processor = DataProcessor(api_loader)
# processor.process()  # Output: Processing data: Data from API: https://api.example.com/data


#PLACEHOLDERS

# @dataclass
# class DataLoader():

#     data_link:DataLink
#     # data_storage:list[DataStorage] = field(default_factory=list)
#     # metadata_storage:list[MetaDataStorage] = field(default_factory=list)
#     data_objects:list[DataStorage|MetaDataStorage] = field(default_factory=list)
    

#     def load_data(self, id=None):

#         loaded_data = self.data_link.load_data()
#         self.data_objects = [self.process_data_item(data_row) for data_row in loaded_data]

#         # loaded_data['id'] = loaded_data['hash'] #TMP
#         # data = {k:v for k,v in loaded_data.items() if k in ['hash', 'uri']}
#         # metadata = {k:v for k,v in loaded_data.items() if k in ['id', 'description', 'tags', 'uri']}
#         # if not self.data_storage:
#         #     self.data_storage.append(DataStorage(**data))
#         # if not self.metadata_storage:
#         #     self.metadata_storage.append(MetaDataStorage(**metadata))

#     def process_data_item(self, data_item_row:dict):
#         data_item_row['id'] = data_item_row['hash']
#         data = {k:v for k,v in data_item_row.items() if k in ['hash', 'uri']}
#         metadata = {k:v for k,v in data_item_row.items() if k in ['id', 'description', 'tags', 'uri']}
#         item_row = {'data': DataStorage(**data), 'metadata': MetaDataStorage(**metadata)}
#         return item_row



 ##
 # 

if __name__ == '__main__':

    b = benedict('tmp22.json', format='json')
    # print(b)

    jd = JSONDataLink(file_path='tmp22.json')
    # dd = jd.load_data()
    dl = DataLoader(data_link=jd)

    dl.load_data()

    # pprint(jd)
    pprint('Before Load')
    
# pprint(dl.metadata_storage.get_as_dict())
    dl.data_objects[0]['data'].load()#works
    dl.data_objects[1]['data'].load(dl.data_objects[1]['data'].uri)#works

    dl.data_objects[0]['data'].save_file("dl_do_0.png")#works
    dl.data_objects[1]['data'].save_file("dl_do_1.jpg")#works

    pprint('END')