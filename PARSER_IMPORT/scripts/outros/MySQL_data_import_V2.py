from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from datetime import timedelta 
import os
import shutil
import warnings

warnings.filterwarnings("ignore") ##Desabilita mensagens de Warning


BASE_DIR='c:/Users/tulio/Desktop/FILES'
SOURCE_DIR= BASE_DIR + '/data'
TARGET_DIR= BASE_DIR + '/imported'

##MYSQL
print("Connecting to MySQL database...")
c = create_engine('mysql+pymysql://root:computer@localhost/db_test')
c.execute('USE db_test;')
print("Connected!")
col_names=['datetime','device_name','MAC', 'type', 'RSSI']

print("Importing data to database...")
list_files = os.listdir(SOURCE_DIR)
for file in os.listdir(SOURCE_DIR):
    df = pd.read_csv(SOURCE_DIR+'/'+file, header=None, error_bad_lines=False, warn_bad_lines=True,  names=col_names,  index_col=False, encoding='ISO-8859–1', engine='python',sep=",") #error_bad_lines=False
    
    #df.MAC=df.MAC.str.strip('+INQ:') # remove +INQ dos MACs
    df['datetime'] =  pd.to_datetime(df['datetime'], errors='coerce')
    df.MAC=df.MAC.str.replace('^.+INQ:', '', regex=True) # remove *+INQ dos MACs
    df.MAC.fillna("0", inplace = True) # substituir NULL por 0 no MAC (evitar erro se MAC cannot be NULL) 
    df.device_name.fillna("0", inplace = True) # substituir NULL por 0 no MAC (evitar erro se deviceID cannot be NULL) 
    #df.reset_index(drop=True, inplace=True) #remover maldito index
    df.to_sql(name='table_test', if_exists='append', con=c, index=False) 
    #c.execute('ALTER TABLE db_test.table_test MODIFY COLUMN `datetime` datetime;')
    shutil.move(SOURCE_DIR+'/'+file, TARGET_DIR)
    print(file)
c.execute("""CREATE TABLE IF NOT EXISTS mac_count(
            datetime datetime DEFAULT NULL,
            device_name varchar(50),
            MAC varchar(50),
            type varchar(50), 
            RSSI varchar(50), 
            count int,
            PRIMARY KEY (device_name,MAC)
            );""")
c.execute("""REPLACE INTO mac_count
             SELECT *,COUNT(MAC)
             FROM db_test.table_test
             GROUP BY device_name,MAC;""")
#c.execute("""CREATE TABLE IF NOT EXISTS mac_count AS
#          SELECT *, COUNT(MAC) AS qtd FROM db_test.table_test 
#         GROUP BY `MAC`;""")

print("Imported!")



