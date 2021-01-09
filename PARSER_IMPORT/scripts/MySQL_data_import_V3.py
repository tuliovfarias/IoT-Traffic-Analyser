#%%
from sqlalchemy import create_engine
import pandas as pd
import os
import shutil
import warnings
import sys

warnings.filterwarnings("ignore") ##Desabilita mensagens de Warning
sys.exit
BASE_DIR='C:\\Google Drive\\CEFET\\TCC\\Programas\\FILES'
SOURCE_DIR= os.path.join(BASE_DIR,'data')
TARGET_DIR= os.path.join(BASE_DIR,'imported')

##MYSQL
print("Connecting to MySQL database...")
c = create_engine('mysql+pymysql://root:computer@localhost/db_test')
c.execute('USE db_test;')
print("Connected!")
col_names=['datetime','device_name','MAC', 'type', 'RSSI']
c.execute("""CREATE TABLE IF NOT EXISTS mac_count(
            datetime datetime DEFAULT '0000-00-00 00:00:00',
            device_name varchar(50),
            MAC varchar(50),
            type varchar(50), 
            RSSI varchar(50), 
            count int,
            PRIMARY KEY (device_name,datetime,MAC)
            );""")
print("Importing data to database...")
list_files = os.listdir(SOURCE_DIR)
if len(list_files)==0:
    print("No files to import!")
else:
    for file in os.listdir(SOURCE_DIR):
        df = pd.read_csv(SOURCE_DIR+'/'+file, header=None, error_bad_lines=False, warn_bad_lines=True,  names=col_names,  index_col=False, encoding='ISO-8859–1', engine='python',sep=",") #error_bad_lines=False
        #df.MAC=df.MAC.str.strip('+INQ:') # remove +INQ dos MACs
        start_datetime=df.at[0,'datetime']
        end_datetime=df.at[len(df.index)-1,'datetime']
        df['datetime'] =  pd.to_datetime(df['datetime'], errors='coerce')
        df.MAC=df.MAC.str.replace('^.+INQ:', '', regex=True) # remove *+INQ dos MACs
        df.MAC.fillna("0", inplace = True) # substituir NULL por 0 no MAC (evitar erro se MAC cannot be NULL) 
        df.device_name.fillna("0", inplace = True) # substituir NULL por 0 no MAC (evitar erro se deviceID cannot be NULL) 
        #df.reset_index(drop=True, inplace=True) #remover maldito index
        df.to_sql(name='table_temp', if_exists='append', con=c, index=False) 
        df.to_sql(name='table_all_scans', if_exists='append', con=c, index=False) 
        #c.execute('ALTER TABLE db_test.table_temp MODIFY COLUMN `datetime` datetime;')
        shutil.move(SOURCE_DIR+'/'+file, TARGET_DIR)
        print(file)
        query_mac_count=("""INSERT INTO mac_count
                    SELECT *,COUNT(MAC)
                    FROM db_test.table_temp
                    WHERE datetime BETWEEN '"""+start_datetime+"' and '"+end_datetime+"""'
                    GROUP BY device_name,MAC;""")
        c.execute(query_mac_count)
        c.execute("TRUNCATE TABLE db_test.table_temp;")
    #c.execute("""CREATE TABLE IF NOT EXISTS mac_count AS
    #          SELECT *, COUNT(MAC) AS qtd FROM db_test.table_test 
    #         GROUP BY `MAC`;""")

    print("Imported!")






