from sqlalchemy import create_engine, String
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, declarative_base
from sqlalchemy.orm import MappedAsDataclass
from sqlalchemy.orm import DeclarativeBase


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orm_models_sqlalchemy import Base, DefaultTable, DataStorageIndexTable



from abc import ABC, abstractmethod

# Step 1: Define an abstract base class (interface) for data loaders
class CRUDDataLinkAbstractBase(ABC): #RAW Data Loader
    @abstractmethod
    def read_all(self):
        pass

class CRUDDataLinksSQL(CRUDDataLinkAbstractBase):
    def __init__(self, db_url: str):
        """
        Initialize the CRUDIndex class with a database URL.

        Args:
            db_url (str): The database URL (e.g., 'sqlite:///example.db', 'postgresql://user:password@localhost/dbname').
        """
        # Initialize the database engine and session
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Set the default table
        self.DataTable = DefaultTable

        # Create the table if it doesn't exist
        Base.metadata.create_all(self.engine)

    def set_data_table(self, table_class):
        """
        Set a new ORM table class for CRUD operations.

        Args:
            table_class: A SQLAlchemy ORM model class.
        """
        if not hasattr(table_class, '__tablename__'):
            raise ValueError("The table class must have a __tablename__ attribute.")
        self.DataTable = table_class
        Base.metadata.create_all(self.engine)  # Ensure the new table is created

    def create(self, values: dict[str, object]):
        """
        Create a new row in the current DataTable.

        Args:
            values (dict[str, Any]): A dictionary of field names and values for the new row.
        """
        new_row = self.DataTable(**values)
        self.session.add(new_row)
        self.session.commit()
        return new_row

    def read_all(self) -> list[object]:
        """Return all rows from the current DataTable."""
        return self.session.query(self.DataTable).all()

    def read(self, filters: dict[str, object]) -> object | None:
        """
        Return a specific row based on filters.

        Args:
            filters (dict[str, Any]): A dictionary of field names and values to filter by.
        """
        query = self.session.query(self.DataTable)
        for field, value in filters.items():
            query = query.filter(getattr(self.DataTable, field) == value)
        return query.first()

    def update(self, filters: dict[str], values: dict[str, object]) -> object | None:
        """
        Update an existing row with new data.

        Args:
            filters (dict[str, Any]): A dictionary of field names and values to filter by.
            values (dict[str, Any]): A dictionary of field names and new values to update.
        """
        row = self.read(filters)
        if row:
            for field, value in values.items():
                setattr(row, field, value)
            self.session.commit()
        return row

# Example usage
if __name__ == "__main__":
    # Replace with your actual database URL
    db_url = 'sqlite:///'  # SQLite example
    crud = CRUDDataLinksSQL(db_url)

    # Use the default table
    crud.create({"id": "1"})
    rows = crud.read_all()
    for row in rows:
        print(row.id)

    # Read a specific row
    row = crud.read({"id": "1"})
    if row:
        print("Found:", row)

    # Update a row
    



    # Switch to the new table
    crud.set_data_table(DataStorageIndexTable)

    # Use the new table
    crud.create({"id": "1", "load_method": "file", "uri": "This is a new table"})
    rows = crud.read_all()
    for row in rows:
        print(row.id, row.uri, row.load_method)

    crud.update({"id": "1"}, {"uri": "http://updated.com", "load_method": "https"})

    # Verify the update
    updated_row = crud.read({"id": "1"})
    if updated_row:
        print("Updated:", updated_row.id, updated_row.uri, updated_row.load_method)
