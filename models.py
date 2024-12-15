import sqlalchemy
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime

dotenv_file = '.env'
load_dotenv(dotenv_file)

# Настройки подключения к базе данных
DB_HOST = os.environ.get("POSTGRES_DBHOST", "127.0.0.1")
DB_PORT = os.environ.get("POSTGRES_DBPORT", "5432")
DB_NAME = os.environ.get("POSTGRES_DBNAME", "postgres")
DB_USER = os.environ.get("POSTGRES_USER", "postgres")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "1234")

DSN = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}'
engine = create_engine(DSN)
engine_table = create_engine(f"{DSN}/{DB_NAME}")


def delete_create_base():
    """Функция удаления и создания ДатаБазы"""
    try:
        with sqlalchemy.create_engine(DSN, isolation_level='AUTOCOMMIT').connect() as connection:
            connection.execute(text(f'DROP DATABASE IF EXISTS {DB_NAME} WITH (FORCE);'))
            connection.execute(text(f'CREATE DATABASE {DB_NAME}'))
        print(f'База данных {DB_NAME} успешно создалась')
    except (sqlalchemy.exc.OperationalError, UnicodeDecodeError) as e:
        print(e)
    except sqlalchemy.exc.ProgrammingError as e:
        print(e)


class Base(DeclarativeBase):

    @property
    def id_dict(self):
        return {"id": self.id}


class Announcement(Base):
    """Модель таблицы объявлений"""
    __tablename__ = 'announcement'
    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    description = Column(String(500), nullable=False)
    author = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class User(Base):
    """Модель таблицы Пользователей"""
    __tablename__ = "app_user"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    password = Column(String(15), nullable=False)
    registration_time = Column(DateTime, default=datetime.now)

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "registration_time": self.registration_time.isoformat(),
        }


def delete_create_table():
    # Создаем таблицу, если ее не существует
    Base.metadata.create_all(bind=engine_table)

    # Создаем сессию для взаимодействия с базой данных
    with sessionmaker(bind=engine_table)() as session:
        new_user = User(name="Maksim", password="1")
        session.add(new_user)
        session.commit()
        print(f'Создана первая тестовая учетная запись')

    with sessionmaker(bind=engine_table)() as session:
        new_announcement = Announcement(title="Test Title", description="Test Description", author="Maksim Velichko")
        session.add(new_announcement)
        session.commit()
        print(f'Создана первая тестовая запись')
