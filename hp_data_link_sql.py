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

class CRUDDataLinkSQL(CRUDDataLinkAbstractBase):
    def __init__(self, db_url: str):
        """
        Initialize the CRUDDataLinkSQL class with a database URL.

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

    def _row_to_dict(self, row) -> dict[str]:
        """
        Convert a SQLAlchemy ORM object to a dictionary.

        Args:
            row: A SQLAlchemy ORM object.

        Returns:
            dict[str]: A dictionary representation of the row.
        """
        return {column.name: getattr(row, column.name) for column in row.__table__.columns}

    def create(self, values: dict[str]):
        """
        Create a new row in the current DataTable.

        Args:
            values (dict[str]): A dictionary of field names and values for the new row.
        """
        new_row = self.DataTable(**values)
        self.session.add(new_row)
        self.session.commit()
        return new_row

    def read_all(self, as_dict: bool = True) -> list[dict[str]] | list:
        """
        Return all rows from the current DataTable.

        Args:
            as_dict (bool): If True, returns results as a list of dictionaries. If False, returns results in their native form.

        Returns:
            list[dict[str]] | list: A list of rows, either as dictionaries or ORM objects.
        """
        rows = self.session.query(self.DataTable).all()
        return [self._row_to_dict(row) for row in rows] if as_dict else rows

    def read(self, id: str, as_dict: bool = True) -> list[dict[str]] | list:
        """
        Return a specific row by id.

        Args:
            id (str): The id of the row to retrieve.
            as_dict (bool): If True, returns results as a list of dictionaries. If False, returns results in their native form.

        Returns:
            list[dict[str]] | list: A list containing the row, either as a dictionary or an ORM object.
        """
        return self._read({"id": id}, as_dict=as_dict)

    def _read(self, filters: dict[str], as_dict: bool = True) -> list[dict[str]] | list:
        """
        Return rows matching the filters.

        Args:
            filters (dict[str]): A dictionary of field names and values to filter by.
            as_dict (bool): If True, returns results as a list of dictionaries. If False, returns results in their native form.

        Returns:
            list[dict[str]] | list: A list of rows, either as dictionaries or ORM objects.
        """
        query = self.session.query(self.DataTable)
        for field, value in filters.items():
            query = query.filter(getattr(self.DataTable, field) == value)
        rows = query.all()
        return [self._row_to_dict(row) for row in rows] if as_dict else rows

    def update(self, id: str, values: dict[str]) -> list[dict[str]]:
        """
        Update a specific row by id with new data.

        Args:
            id (str): The id of the row to update.
            values (dict[str]): A dictionary of field names and new values to update.

        Returns:
            list[dict[str]]: A list containing the updated row as a dictionary.
        """
        return self._update({"id": id}, values)

    def _update(self, filters: dict[str], values: dict[str]) -> list[dict[str]]:
        """
        Update existing rows with new data and return the updated rows as a list of dictionaries.

        Args:
            filters (dict[str]): A dictionary of field names and values to filter by.
            values (dict[str]): A dictionary of field names and new values to update.

        Returns:
            list[dict[str]]: A list of updated rows as dictionaries.
        """
        rows = self._read(filters, as_dict=False)
        if rows:
            for row in rows:
                for field, value in values.items():
                    setattr(row, field, value)
            self.session.commit()
        return self._read(filters)

    def delete_all(self):
        """Delete all rows in the current DataTable."""
        self.session.query(self.DataTable).delete()
        self.session.commit()

    def delete(self, id: str):
        """
        Delete a specific row by id.

        Args:
            id (str): The id of the row to delete.
        """
        self._delete({"id": id})

    def _delete(self, filters: dict[str]):
        """
        Delete rows matching the filters.

        Args:
            filters (dict[str]): A dictionary of field names and values to filter by.
        """
        rows = self._read(filters, as_dict=False)
        if rows:
            for row in rows:
                self.session.delete(row)
            self.session.commit()

    def tempf(self, t:str = 'tmp'):
        """
        TMP FUNC

        :param t: String

        :return: The same string

        """
        print(f'tmp {t}')
        return t

    
class CRUDDataStorageIndexSQL(CRUDDataLinkSQL):
    def __init__(self, db_url):
        super().__init__(db_url)
        self.set_data_table(DataStorageIndexTable)


# Example usage

# Example usage
if __name__ == "__main__":
    # Replace with your actual database URL
    db_url = 'sqlite://'  # SQLite example
    crud = CRUDDataLinkSQL(db_url)

    # Use the default table (only 'id' field)
    crud.create({"id": "1"})
    crud.create({"id": "2"})

    # Read all rows as dictionaries
    print("All rows (as dictionaries):")
    rows = crud.read_all(as_dict=True)
    for row in rows:
        print(row)

    # Read a specific row as a dictionary
    print("Row with id=1 (as dictionary):")
    rows = crud.read("1", as_dict=True)
    for row in rows:
        print(row)

    # Update a specific row
    print("After updating row with id=1:")
    updated_rows = crud.update("1", {"id": "1_updated"})
    for row in updated_rows:
        print(row)

    # Delete a specific row
    crud.delete("1_updated")
    print("After deleting row with id=1_updated:")
    rows = crud.read_all(as_dict=True)
    for row in rows:
        print(row)

    # # Switch to the new table (with 'id', 'uri', 'load_method' fields)
    # crud.set_data_table(NewTable)

    # # Use the new table
    # crud.create({"id": "1", "uri": "http://example.com", "load_method": "http"})
    # crud.create({"id": "2", "uri": "http://example.org", "load_method": "https"})

    # # Read all rows in the new table as dictionaries
    # print("All rows in the new table (as dictionaries):")
    # rows = crud.read_all(as_dict=True)
    # for row in rows:
    #     print(row)

    # # Update a specific row in the new table
    # print("After updating row with id=1 in the new table:")
    # updated_rows = crud.update("1", {"uri": "http://updated.com", "load_method": "https"})
    # for row in updated_rows:
    #     print(row)
        
        
        
    cdi = CRUDDataStorageIndexSQL('sqlite://')
    cdi.create({'id': '1','load_method': 'local', 'uri': 'uri1'})
    cdi.create({'id': '2', 'load_method': 'remote', 'uri': 'uri2'})
    cdi.update('2', {'load_method':'s3'})

    pa = cdi.read_all()
    p = cdi.read('1')
    print(pa)
    print(p)
    # print(p.__dict__)
    

    cdi.tempf('34234')


