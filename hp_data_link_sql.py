from sqlalchemy import create_engine, String
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, declarative_base
from sqlalchemy.orm import MappedAsDataclass
from sqlalchemy.orm import DeclarativeBase

from abc import ABC, abstractmethod

# Step 1: Define an abstract base class (interface) for data loaders
class CRUDDataLink(ABC): #RAW Data Loader
    @abstractmethod
    def read_all(self):
        pass


class CRUDDataLinkSQLStorageIndex(CRUDDataLink):



    # Define the ORM model using MappedAsDataclass


    def __init__(self, db_url: str):
        """
        Initialize the CRUDIndex class with a database URL.

        Args:
            db_url (str): The database URL (e.g., 'sqlite:///example.db', 'postgresql://user:password@localhost/dbname').
        """

        class Base(DeclarativeBase):
            pass

        class IndexTable(MappedAsDataclass, Base):
            """ORM model for the index_table."""
            __tablename__ = 'index_table'

            id: Mapped[str] = mapped_column(String, primary_key=True)
            uri: Mapped[str] = mapped_column(String)
            load_method: Mapped[str] = mapped_column(String)
        # Initialize the database engine and session
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Define the base class for ORM models
        # self.Base = declarative_base()
        # self.Base = declarative_base()



        self.IndexTable = IndexTable

        # Create the table if it doesn't exist
        # self.Base.metadata.create_all(self.engine)
        Base.metadata.create_all(self.engine)

    def create(self, id: str, uri: str, load_method: str) -> 'IndexTable':
        """Create a new row in the index_table."""
        new_row = self.IndexTable(id=id, uri=uri, load_method=load_method)
        self.session.add(new_row)
        self.session.commit()
        return new_row

    def read_all(self) -> list['IndexTable']:
        """Return all rows from the index_table."""
        return self.session.query(self.IndexTable).all()

    def read(self, id: str) -> 'IndexTable':
        """Return a specific row by id."""
        return self.session.query(self.IndexTable).filter_by(id=id).first()

    def update(self, id: str, uri: str = None, load_method: str = None) -> 'IndexTable':
        """Update an existing row with new data."""
        row = self.session.query(self.IndexTable).filter_by(id=id).first()
        if row:
            if uri:
                row.uri = uri
            if load_method:
                row.load_method = load_method
            self.session.commit()
        return row

# Example usage
if __name__ == "__main__":
#     # Replace with your actual database URL
    # db_url = 'sqlite:///'  # SQLite example
    db_url = 'sqlite:///example.db'  # SQLite example
#     # db_url = 'postgresql://user:password@localhost/dbname'  # PostgreSQL example
    crud = CRUDDataLinkSQLStorageIndex(db_url)

#     # Create a new row
#     # crud.create(id="12", uri="http://example.com12", load_method="http")

#     # Read all rows
#     rows = crud.read_all()
#     for row in rows:
#         print(row.id, row.uri, row.load_method)

#     # Read a specific row
#     row = crud.read("1")
#     if row:
#         print("Found:", row.id, row.uri, row.load_method)

#     # Update a row
#     crud.update(id="1", uri="http://updated.com", load_method="https")

#     # Verify the update
#     updated_row = crud.read("1")
#     if updated_row:
#         print("Updated:", updated_row.id, updated_row.uri, updated_row.load_method)