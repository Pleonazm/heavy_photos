import json
import hashlib
from pathlib import Path
import uuid

from qdrant_client import QdrantClient, models

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

from ai_client_wrapper import AI_Client_Call_Wrapper
from hp_basic_crud_interface import BasicCRUDInterface

class QdrantWrapper(BasicCRUDInterface):
    def __init__(self, host_url:str='localhost:6333', collection_name:str="my_collection", vector_size:int=1536, emb_fields:list=None,
                 ai_wrapper=None, memory_only:bool=False):
        """
        Initializes Qdrant client and collection.
        """
        if memory_only:
            self.client = QdrantClient(':memory:')
        else:
            self.client = QdrantClient(host_url) #self.client = QdrantClient(host=host, port=port)


        self.collection_name = collection_name
        self.vector_size = vector_size
        self.ai_wrapper:AI_Client_Call_Wrapper = ai_wrapper
        if not emb_fields:
            self.emb_fields = ['tags', 'description']
        
        self.uuid_namespace = self._generate_uuid_namespace(self.collection_name, uuid.NAMESPACE_OID)

        

        # Create collection if it doesn't exist
        self.make()

        # self.client.recreate_collection(
        #     collection_name=self.collection_name,
        #     vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
        # )
        


    def make(self):
        if not self.client.collection_exists(collection_name=self.collection_name):
            print(f"Creating {self.collection_name}...")
            self.client.create_collection(collection_name=self.collection_name,
        vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
    )
        # return super().make()
    
    def remake(self, data=None):
        return super().remake(data)
    
    def unmake(self):
        return super().unmake()
    
    def _generate_uuid_namespace(self, seed: str, base_namespace: uuid.UUID = uuid.NAMESPACE_OID) -> uuid.UUID:
        """
        Creates a custom namespace UUID from a seed string (e.g., your app name).
        Uses UUIDv5 (SHA-1) for deterministic generation.
        """
        namespace = uuid.uuid5(base_namespace, seed)
        self.uuid_namespace = namespace
        return namespace
    
    def _generate_uuid(self, uuid_base_str: str, namespace: uuid.UUID=None) -> uuid.UUID:
        """
        Generates a UUIDv5 in a custom namespace for a given name (e.g., a user ID or document hash).
        """
        if not namespace:
            namespace = self.uuid_namespace
        return str(uuid.uuid5(namespace, uuid_base_str))
    
    def _validate_id_uuid(self,id):
        if not self._is_valid_uuid(id):#change into exceptions?
            return self._generate_uuid(id)
        else:
            return id



    

    def add(self, data, id=None, raw_embeddings=False, metadata=None):#logical id, usually hash
        """Adds data"""
        id = self._validate_id_uuid(id)
        if self.get(id):
            raise ValueError('ID already in present')
        else:
            self.update(data, id=id, raw_embeddings=raw_embeddings, metadata=metadata)
        # if raw_embeddings:
        #     vector = raw_embeddings
        #     # self._upsert(id=int(data['id'][:16], 16), vector=raw_embeddings, payload=data)
        # else:
        #     # raise ValueError('No emed')#Temp
        #     emb_arr = self._parse_for_embeddings(data)
        #     vector = self.ai_wrapper.call_text_embeddings(emb_arr)
        # self._upsert(id=id, vector=raw_embeddings, payload=data)

        # if raw_embeddings:
        #     self._add_raw_embeddings(data)
        #     q_vector=data
        #     # point_id= self._create_id_from_any_str(str(data))
        # else:
        #     if (not data['id']) or (not data['description']):
        #         print('No data')#change into exception later?
        #         raise ValueError('QDrant Wrapper.add: No data')
        #     # q_vector=self._get_embeddings(data['description'])
        #     q_vector=self._create_embeddings(self._create_vector_description(data))
        #     # point_id = self._create_id_from_hash(data['id'])
        # point_id = int(data['id'][:16], 16)
        # self.client.upsert(
        #         collection_name=self.collection_name,
        #                 points=[
        #                 PointStruct(
        #     # id=self._create_id_from_str(data['id']),
        #                 id = point_id,
        #                 vector=q_vector,
        #                 payload=data,
        #                 )])

    # def _add_raw_embeddings(self, data):#not done, not tested

    #     # point_id = self._create_id_from_any_str(str(data))
    #     point_id = point_id = int(data['id'][:16], 16)
    #     self.client.upsert(
    #     collection_name=self.collection_name,
    #         points=[
    #             PointStruct(
    #             # id=self._create_id_from_str(data['id']),
    #             id = point_id,
    #             vector=data,
    #             # payload=data,
    #                         )])


    
    def get(self, id):#Logical ID (usually hash), not UUID in collection
        """Reads a single item by ID."""
        # if not self._is_valid_uuid(id):
        #     id = self._generate_uuid(id)
        id = self._validate_id_uuid(id)
        return self.client.retrieve(collection_name=self.collection_name, ids=[id])
        

            # raise ValueError('No valid ID')
    
    def get_all(self):
        """Reads all data from the collection."""
        return self.client.scroll(collection_name=self.collection_name, limit=1000)[0]
    
    def _is_valid_uuid(self, uuid_str: str) -> str|bool:
        try:
            # Convert the string to a UUID (this validates formatting)
            uuid_obj = uuid.UUID(uuid_str)
            # Compare the normalized string (lowercase, hyphens) to the input
            # return str(uuid_obj) == uuid_str.lower()
            return uuid_str.lower()
        except ValueError:
            return False
    
    def find(self, data:dict|list|str, raw_embeddings=None):#if dict, search by field=value, if list by tags, if string by description

        if raw_embeddings:
            # q_vector=data
            return self._find_by_emb(raw_embeddings)
        else:
            emb_txt = self._parse_for_embeddings(data)
            q_vector=self._create_embeddings(emb_txt)


        results = self.client.search(collection_name=self.collection_name,
                                    query_vector=q_vector, limit=3,)
                    
        return results
    
    def _find_by_emb(self, data):
        results = self.client.search(collection_name=self.collection_name,
                                    query_vector=data, limit=3,)
                    
        return results

    def _parse_for_embeddings(self, data:dict):

        emb_list = []
        try:
            for field in self.emb_fields:
                emb_list + list(data[field])
        except KeyError:
            print(f"Parse for Embeddigns: No Key for {field}")
        
        emb_txt = ', '.join(emb_list)

        return emb_txt



    # def update(self, id, data, metadata=None, raw_embeddings=False):#to rewrite
    def update(self,data, metadata=None, raw_embeddings=None, id=None):#to rewrite
        """Updates or inserts an item in the collection."""
        id = self._validate_id_uuid(id)
        if raw_embeddings:
            vector = raw_embeddings
            
        else:#Temporary??
            vector, info = self._create_embeddings(data)
            # emb_arr = data['tags']
            # emb_arr.append(data['description'])
            # emb_txt = self._parse_for_embeddings(data)
            # vector, info = self.ai_wrapper.call_text_embeddings(emb_txt)

        self._upsert(id=id, vector=raw_embeddings, payload=data)

            # raise ValueError('No emed')#Temp
        # else:
        #     v_desc = self._create_vector_description(data)
        #     upd_vector = self._create_embeddings(data)
        # self.client.upsert(
        #     collection_name=self.collection_name,
        #     points=[
        #         models.PointStruct(id=int(data['id'][:16], 16), vector=upd_vector, payload=data)
        #         # models.PointStruct(id=self._create_id_from_hash(data['id']), vector=upd_vector, payload=data)
        #         # models.PointStruct(id=self._create_id_from_hash(data['id']), vector=upd_vector, payload=data)
        #     ]
        # )

    def delete(self, item_id):
        """Deletes a single item by ID."""
        self.client.delete(collection_name=self.collection_name,
                           points_selector=models.PointIdsList(ids=[self._create_id_from_hash(item_id)]))

    def delete_all(self):
        """Removes all data but keeps the collection."""
        self.client.delete(collection_name=self.collection_name, points_selector=models.FilterSelector(filter={}))

    ##########

    def _create_embeddings(self, data_to_emb:str|list):
        if isinstance(data_to_emb,list):
            data_to_emb = self._parse_for_embeddings(data_to_emb)

        result, info = self.ai_wrapper.call_text_embeddings(data_to_emb)
        return result, info
    
    def _create_vector_description(self, data:dict) -> str:#temporary
        vect_str = json.dumps(data)

        return vect_str
    
    def _create_id_from_hash(self, input:str) ->int:
        return int(input) % (2**63)#usually to get id from hash
    
    def _create_id_from_any_str(self, input:str) ->int:
        hash = hashlib.sha256(str(input).encode()).hexdigest()
        integer_value = int(hash, 16)
        return int(integer_value) % (2**63)#usually to get id from hash
    
    # def _parse_payload_to_upsert(self, payload_data):

    
    def _upsert(self, id, vector, payload):
            payload = {k:v for k,v in payload.items() if k not in  ['embeddings', 'raw_data']}#tmp for testing
            self.client.upsert(collection_name=self.collection_name,
            points=[PointStruct(id=id,vector=vector, payload=payload)]
                                    )
    
    

    # def create(self, item_id, vector, metadata=None):
    #     self.update(item_id, vector, metadata)

    # def read_all(self):
    #     """Reads all data from the collection."""ai_client
    #     return self.client.scroll(collection_name=self.collection_name, limit=1000)[0]

    # def read(self, item_id):
    #     """Reads a single item by ID."""
    #     return self.client.retrieve(collection_name=self.collection_name, ids=[item_id])



    


# Example usage
if __name__ == "__main__":
    
    # qdrant = QdrantWrapper(collection_name="test_collection", vector_size=128, memory_only=True)
    qdrant = QdrantWrapper(collection_name="test_collection", memory_only=True)

    # OLD TESTS
    
    tmp_test_data = json.loads(Path('tests/data/full_dump.json').read_text())
    test_data = []
    for ob in tmp_test_data:
        if ob['embeddings'] == []:
            ob['embeddings'] = [0.1] * 1536
        test_data.append(ob)
    # print(tmp_test_data)#Loaded ok

    # qdrant._upsert(id=int(tmp_test_data[0]['id'][:16], 16), vector=tmp_test_data[0]['embeddings'],payload=tmp_test_data[0])

    # Insert/update an item
    # # qdrant.update(1, vector=[0.1] * 128, metadata={"name": "Item 1"})
    for ob in test_data:
    # #    qdrant.update(id=ob['id'], data=None, metadata=None, raw_embeddings=ob['embeddings']) 
        qdrant.add(data=ob, metadata=None, raw_embeddings=ob['embeddings'], id=ob['id'])
        # qdrant._upsert(id=int(ob['id'][:16], 16), vector=ob['embeddings'],payload=ob)
    
    # qdrant.add(data=test_data[0], metadata=None, raw_embeddings=test_data[0]['embeddings'])
    # Read all items
    all_items = qdrant.get_all()
    
    # Read single item
    # item = qdrant.get(int(test_data[0]['id'][:16], 16))
    item = qdrant.get(test_data[0]['id'])
    print(item[0].payload)
    
    # Delete item
    # qdrant.delete(1)


    # print(qdrant.get_all())

    print(qdrant.find(data=None, raw_embeddings=tmp_test_data[1]['embeddings']))



    
    # Clear collection
    qdrant.delete_all()

    #########