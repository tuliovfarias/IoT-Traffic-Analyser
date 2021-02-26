#%%
##Limpar variáveis
#from IPython import get_ipython
#get_ipython().magic('reset -sf')

from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from datetime import timedelta 

##MYSQL
c = create_engine('mysql+pymysql://root:computer@localhost/db_test')
c.execute('USE db_test;')
df_plot1=pd.DataFrame()
df_plot2=pd.DataFrame()

start_time= datetime.datetime(2019, 1, 10, 18, 20) #start_time= '2020-06-22 23:15:00'
end_time= datetime.datetime(2019, 1, 10, 18, 55) #end_time = '2020-06-23 00:45:00'
devices=["'A1'","'A2'","'A3'"]
time_slot= timedelta(minutes=5, hours=0)

# SCANS TOTAL
for device in devices:
    start_time_temp=start_time
    while (start_time_temp<end_time):
        end_time_temp= start_time_temp + time_slot
        query1= "SELECT IFNULL (SUM(count),0) FROM db_test.mac_count WHERE datetime >= '"+ str(start_time_temp) +"' and datetime < '"+ str(end_time_temp)+"'"+" and device_name IN ("+device+")"
        query2= "SELECT IFNULL (COUNT(MAC),0) FROM db_test.mac_count WHERE datetime >= '"+ str(start_time_temp) +"' and datetime < '"+ str(end_time_temp)+"'"+" and device_name IN ("+device+")"
        response1=c.execute(query1)
        response2=c.execute(query2)
        for row in response1.fetchall():
            df_plot1=df_plot1.append({'datetime': start_time_temp.strftime('%d/%m\n%H:%M'), 'num_scans': row[0]}, ignore_index=True)
        for row in response2.fetchall():
            df_plot2=df_plot2.append({'datetime': start_time_temp.strftime('%d/%m\n%H:%M'), 'num_cars': row[0]*8.2115+91.3910}, ignore_index=True)
        start_time_temp= start_time_temp + time_slot
    #plt.plot(df_plot['datetime'],df_plot['num_cars'],marker='o', ) #ds='steps'

    #PLOT IN THE SAME CHART
    #plt.bar(df_plot1['datetime'],df_plot1['num_scans'], align='edge', width=0.9) #número de scans a cada slot de tempo (barra azul)
    plt.title('Number of cars')
    plt.plot(df_plot2['datetime'],df_plot2['num_cars']) #número de carros a cada slot de tempo (barra laranja)
    plt.legend(devices)
    df_plot1.drop(df_plot1.index, inplace=True) #limpar DF
    df_plot2.drop(df_plot2.index, inplace=True) #limpar DF
plt.show()

#PLOT IN DISTINCT CHARTS
# fig, axs = plt.subplots(nrows=2, sharex=True)
# fig.suptitle('Total of scans and number of distinct scans')
# #axs[0].bar(df_plot1['datetime'],df_plot1['num_scans'], align='edge', width=0.9) #número de scans a cada slot de tempo 
# axs[0].plot(df_plot4['datetime'],df_plot4['num_cars']) #número de scans a cada slot de tempo 
# axs[1].plot(df_plot2['datetime'],df_plot2['num_cars']) #número de carros a cada slot de tempo 
