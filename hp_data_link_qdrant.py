from qdrant_client import QdrantClient, models

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

from ai_client_wrapper import AI_Client_Call_Wrapper
from hp_basic_crud_interface import BasicCRUDInterface

class QdrantWrapper(BasicCRUDInterface):
    def __init__(self, host="localhost", port=6333, collection_name="my_collection", vector_size=128, ai_wrapper=None, memory_only=False):
        """
        Initializes Qdrant client and collection.
        """
        if memory_only:
            self.client = QdrantClient(':memory:')
        else:
            self.client = QdrantClient(host=host, port=port)

        self.collection_name = collection_name
        self.vector_size = vector_size
        
        # Create collection if it doesn't exist
        self.make()

        # self.client.recreate_collection(
        #     collection_name=self.collection_name,
        #     vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
        # )
        self.ai_wrapper:AI_Client_Call_Wrapper = ai_wrapper


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
    
    def add(self, data):

        if (not data['id']) and (not data['descriprion']):
            print('No data')#change into exception later?
        else:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                    id=data['id'],
                    vector=self._get_embeddings(data['description']),
                    payload=data,
                                )])   
    
    def get(self, id):
        """Reads a single item by ID."""
        return self.client.retrieve(collection_name=self.collection_name, ids=[id])
    
    def get_all(self):
        """Reads all data from the collection."""
        return self.client.scroll(collection_name=self.collection_name, limit=1000)[0]
    
    def find(self, data):
        results = self.client.search(collection_name=self.collection,
                                    query_vector=self._get_embeddings(data), limit=3,)
                    
        return results



    def update(self, item_id, vector, metadata=None):#to rewrite
        """Updates or inserts an item in the collection."""
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(id=item_id, vector=vector, payload=metadata or {})
            ]
        )

    def delete(self, item_id):
        """Deletes a single item by ID."""
        self.client.delete(collection_name=self.collection_name, points_selector=models.PointIdsList(ids=[item_id]))

    def delete_all(self):
        """Removes all data but keeps the collection."""
        self.client.delete(collection_name=self.collection_name, points_selector=models.FilterSelector(filter={}))

    ##########

    def _get_embeddings(self, txt_to_emb:str):
        result, info = self.ai_wrapper.call_text_embeddings(txt_to_emb)
        return result
    
    

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
    
    qdrant = QdrantWrapper(collection_name="test_collection", vector_size=128, memory_only=True)

    # OLD TESTS
    



    # Insert/update an item
    qdrant.update(1, vector=[0.1] * 128, metadata={"name": "Item 1"})
    
    # Read all items
    print(qdrant.read_all())
    
    # Read single item
    print(qdrant.read(1))
    
    # Delete item
    qdrant.delete(1)
    
    # Clear collection
    qdrant.delete_all()
