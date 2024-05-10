from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Date, Time, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine.url import URL

engine_url = URL.create(
    drivername="mysql+pymysql",
    username="YourID", # YourID
    password="YourPW",  # YourPW
    host="localhost",
    port=3306,
    database="simulator_tempcap"
)

engine = create_engine(engine_url)

Base = declarative_base()

#### DB-model
class TempCap(Base):
    __tablename__ = 'simulator_tempcap'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    time = Column(Time)
    sampletime = Column(Integer)
    temp = Column(Float)
    adc = Column(Integer)
    capacitance = Column(Float)


#### Apply metadata
Base.metadata.create_all(engine)

#### Create a session
Session = sessionmaker(bind=engine)