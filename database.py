import datetime
from dataclasses import dataclass

from sqlalchemy import create_engine, Column, Integer, String, Sequence, DateTime, Boolean, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# 上传文章页模型
class TelegraphPageInfo(Base):
    __tablename__ = 'telegraph_page_info'
    id = Column(Integer, Sequence('page_id_seq'), primary_key=True)

    article_title = Column(String)
    article_link = Column(String)
    image_folder_name = Column(String)
    image_counts = Column(Integer)
    images_src = Column(String)

    created_time = Column(DateTime)
    update_time = Column(DateTime)


# 用户模型
class TelegraphUserInfo(Base):
    __tablename__ = 'telegram_user_info'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)

    short_name = Column(String)
    author_name = Column(String)
    author_url = Column(String)
    access_token = Column(String)
    auth_url = Column(String)

    created_time = Column(DateTime)
    update_time = Column(DateTime)


@dataclass
class PageInfo:
    article_title: str
    article_link: str
    image_folder_name: str
    image_counts: int
    images_src: str

    created_time: datetime
    update_time: datetime


@dataclass
class UserInfo:
    short_name: str
    author_name: str
    author_url: str
    access_token: str
    auth_url: str

    created_time: datetime
    update_time: datetime


# 设置SQLite数据库引擎
# data.db是数据库文件名
engine = create_engine('sqlite:///data/data.db')

# 创建表
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

database = Session()

if __name__ == '__main__':
    # just for test
    # fake_datas = generate_fake_data()

    # Add fake data to the database
    # database.add_all(fake_datas)
    # database.commit()
    page_info = database.query(TelegraphPageInfo).order_by(TelegraphPageInfo.id.desc()).first()
    if page_info:
        print(f"{page_info.id}")
