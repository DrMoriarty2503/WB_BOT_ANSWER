from sqlalchemy import BigInteger, String, Integer, Boolean, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, async_session

engine = create_async_engine(url='postgresql+asyncpg://имя:пароль@хост/название_бд')

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    user_name: Mapped[str] = mapped_column(String(30))
    user_group: Mapped[str] = mapped_column(String(30), default='')

class User_Templates(Base):
    __tablename__ = 'user_templates'
    id: Mapped[int] = mapped_column(primary_key =True )
    tg_user_id = mapped_column(BigInteger)
    template_name = mapped_column(String(100))
    template_text = mapped_column(String(300))
    template_rating = mapped_column(Integer)
    template_product = mapped_column(String(30))
    all_stars = mapped_column(Boolean, default=False)  # Поле для всех звезд
    all_products = mapped_column(Boolean, default=False)  # Поле для всех товаров

class User_Modes(Base):
    __tablename__ = 'user_modes'
    id: Mapped[int] = mapped_column(primary_key =True )
    tg_user_id = mapped_column(BigInteger)
    mode_rating = mapped_column(Integer)
    mode_auto = mapped_column(Boolean, default=False)

class Answers(Base):
    __tablename__ = 'answers'
    id: Mapped[int] = mapped_column(primary_key =True )
    review_id = mapped_column(String(50))
    answer = mapped_column(String(500))

async def async_main ():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

