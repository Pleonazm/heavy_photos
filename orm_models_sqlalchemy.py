from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import MappedAsDataclass

from sqlalchemy import String

# from sqlalchemy.orm import declarative_base
# from sqlalchemy.orm import sessionmaker

# from sqlalchemy import create_engine
# from sqlalchemy.orm import Mapped, mapped_column, declarative_base
# from sqlalchemy.orm import MappedAsDataclass

class Base(DeclarativeBase):
    """Base class for declarative models in SQLAlchemy 2.0."""
    pass


class DefaultTable(MappedAsDataclass, Base):
    """Default ORM model for the table."""
    __tablename__ = 'default_table'

    id: Mapped[str] = mapped_column(String, primary_key=True)


class DataStorageIndexTable(MappedAsDataclass, Base):
    """ORM model for the Data Storage Index."""
    __tablename__ = 'data_storage_index_table'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    uri: Mapped[str] = mapped_column(String)
    load_method: Mapped[str] = mapped_column(String)


class MetaDataStorageTable(MappedAsDataclass, Base):
    """ORM model for the index_table."""
    __tablename__ = 'data_table'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    uri: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    mime: Mapped[str] = mapped_column(String)








# # Initialize the database engine and session
# self.engine = create_engine(db_url)
# self.Session = sessionmaker(bind=self.engine)
# self.session = self.Session()