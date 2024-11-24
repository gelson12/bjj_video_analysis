# database.py

from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import declarative_base, sessionmaker
import logging

Base = declarative_base()

class PoseData(Base):
    __tablename__ = 'pose_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    frame = Column(Integer, index=True)
    landmark_id = Column(Integer)
    x = Column(Float)
    y = Column(Float)
    visibility = Column(Float)
    position_name = Column(String)  # Added position_name column

class Database:
    def __init__(self, db_config):
        """
        Initialize the database connection.
        """
        try:
            db_type = db_config.get('db_type', 'sqlite')
            if db_type == 'postgres':
                user = db_config['db_user']
                password = db_config['db_password']
                host = db_config['db_host']
                port = db_config['db_port']
                db_name = db_config['db_name']
                self.engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db_name}')
            else:
                db_name = db_config['db_name']
                self.engine = create_engine(f'sqlite:///{db_name}')
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            self.session = self.Session()
            logging.info(f"Connected to database '{db_name}' successfully.")
        except Exception as e:
            logging.exception("Failed to initialize the database.")
            raise e

    def create_tables(self):
        """
        Create database tables if they do not exist.
        """
        try:
            Base.metadata.create_all(self.engine)
            logging.info("Database tables created successfully.")
        except Exception as e:
            logging.exception("Failed to create database tables.")
            raise e

    def insert_pose_data(self, data):
        """
        Insert pose data into the database.

        Args:
            data (list of dict): List of pose data dictionaries.
        """
        try:
            records = [PoseData(**item) for item in data]
            self.session.bulk_save_objects(records)
            self.session.commit()
            logging.info(f"Inserted {len(records)} records into the database.")
        except Exception as e:
            logging.exception("Failed to insert pose data into the database.")
            self.session.rollback()
            raise e

    def close(self):
        """
        Close the database session.
        """
        try:
            self.session.close()
            logging.info("Database session closed.")
        except Exception as e:
            logging.exception("Failed to close the database session.")
            raise e
