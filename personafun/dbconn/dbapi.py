from personafun.dbconn.dbengine import Session
from personafun.dbconn.dbengine import TempCap


def apiClean():
    with Session.begin() as session:
        session.query(TempCap).delete()

def countTempCap():
    with Session.begin() as session:
        rows = session.query(TempCap).count()
    return rows

def createTempCap(dataset:list):
    newTempCap = TempCap(date=dataset[0], 
                            time=dataset[1], 
                            sampletime=dataset[2], 
                            temp=dataset[3],
                            adc=dataset[4],
                            capacitance=dataset[5])
    with Session.begin() as session:
        session.add(newTempCap)

def readTempCap():
    with Session.begin() as session:
        db_record = session.query(TempCap).order_by(TempCap.id.desc()).first()
        res_data = [db_record.temp,db_record.adc,db_record.capacitance]
        return res_data
