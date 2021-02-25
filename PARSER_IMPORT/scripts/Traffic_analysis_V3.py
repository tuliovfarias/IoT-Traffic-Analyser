#%%
##Limpar variáveis
from IPython import get_ipython
get_ipython().magic('reset -sf')

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
df_plot3=pd.DataFrame()
df_plot4=pd.DataFrame()
start_time= datetime.datetime(2019, 1, 10, 18, 20) #start_time= '2020-06-22 23:15:00'
end_time= datetime.datetime(2019, 1, 10, 18, 55) #end_time = '2020-06-23 00:45:00'
devices="'A1'"
device="'A2'"
time_slot= timedelta(minutes=5, hours=0)

# SCANS TOTAL
while (start_time<end_time):
    end_time_temp= start_time + time_slot
    #string= "SELECT * FROM db_test.mac_count WHERE datetime >= '"+ str(start_time) +"' and datetime < '"+ str(end_time_temp)+"'"
    query1= "SELECT IFNULL (SUM(count),0) FROM db_test.mac_count WHERE datetime >= '"+ str(start_time) +"' and datetime < '"+ str(end_time_temp)+"'"+" and device_name IN ("+devices+")"
    query2= "SELECT IFNULL (COUNT(MAC),0) FROM db_test.mac_count WHERE datetime >= '"+ str(start_time) +"' and datetime < '"+ str(end_time_temp)+"'"+" and device_name IN ("+devices+")"
    
    query3= "SELECT IFNULL (SUM(count),0) FROM db_test.mac_count WHERE datetime >= '"+ str(start_time) +"' and datetime < '"+ str(end_time_temp)+"'"+" and device_name IN ("+device+")"
    query4= "SELECT IFNULL (COUNT(MAC),0) FROM db_test.mac_count WHERE datetime >= '"+ str(start_time) +"' and datetime < '"+ str(end_time_temp)+"'"+" and device_name IN ("+device+")"
    #query1= "SELECT IFNULL (SUM(count),0) FROM db_test.mac_count WHERE datetime >= '"+ str(start_time) +"' and datetime < '"+ str(end_time_temp) +"' GROUP BY UNIX_TIMESTAMP(datetime) DIV 300 "
    #query2= "SELECT IFNULL (COUNT(MAC),0) FROM db_test.mac_count WHERE datetime >= '"+ str(start_time) +"' and datetime < '"+ str(end_time_temp) +"' GROUP BY UNIX_TIMESTAMP(datetime) DIV 300 "

    response1=c.execute(query1)
    response2=c.execute(query2)

    response3=c.execute(query3)
    response4=c.execute(query4)

    for row in response1.fetchall():
        df_plot1=df_plot1.append({'datetime': start_time.strftime('%d/%m\n%H:%M'), 'num_scans': row[0]}, ignore_index=True)
    for row in response2.fetchall():
        df_plot2=df_plot2.append({'datetime': start_time.strftime('%d/%m\n%H:%M'), 'num_cars': row[0]}, ignore_index=True)
    for row in response3.fetchall():
        df_plot3=df_plot3.append({'datetime': start_time.strftime('%d/%m\n%H:%M'), 'num_scans': row[0]}, ignore_index=True)
    for row in response4.fetchall():
        df_plot4=df_plot4.append({'datetime': start_time.strftime('%d/%m\n%H:%M'), 'num_cars': row[0]}, ignore_index=True)
    start_time= start_time + time_slot
#plt.plot(df_plot['datetime'],df_plot['num_cars'],marker='o', ) #ds='steps'

#PLOT IN THE SAME CHART
#plt.bar(df_plot1['datetime'],df_plot1['num_scans'], align='edge', width=0.9) #número de scans a cada slot de tempo (barra azul)
plt.plot(df_plot4['datetime'],df_plot4['num_cars']) #número de scans a cada slot de tempo (barra azul)
plt.plot(df_plot2['datetime'],df_plot2['num_cars']) #número de carros a cada slot de tempo (barra laranja)

#PLOT IN DISTINCT CHARTS
# fig, axs = plt.subplots(nrows=2, sharex=True)
# fig.suptitle('Total of scans and number of distinct scans')
# #axs[0].bar(df_plot1['datetime'],df_plot1['num_scans'], align='edge', width=0.9) #número de scans a cada slot de tempo 
# axs[0].plot(df_plot4['datetime'],df_plot4['num_cars']) #número de scans a cada slot de tempo 
# axs[1].plot(df_plot2['datetime'],df_plot2['num_cars']) #número de carros a cada slot de tempo 
plt.show()

#i=1
#count_cars=[]
#cars=0
#
#for row in x.fetchall():
#    df2=df2.append({'datetime': row[4], 'num_cars': row[5]}, ignore_index=True)
#    if (row[4] > time_aux):
#         time_aux=time_aux+timedelta(minutes=min_delta, hours=hour_delta)
#         count_cars.append(cars)
#         cars=0
#    else: 
#        cars=cars+row[5]

#plt.plot(df2['datetime'], df2['num_cars'],marker='o')
#plt.show()

#CREATE TABLE mac_count_select AS 

## ITERAÇÃO
#hour_delta=0
#min_delta=5
##iterations=int((end_time-start_time)/timedelta(minutes=min_delta, hours=hour_delta))
#
#i=1
#
#df_plot = pd.DataFrame(columns=['num_car','datetime'])
#
#time_aux=start_time
#
#while (i<len(plot_time.index)):
#    time_aux=time_aux+timedelta(minutes=min_delta, hours=hour_delta)
#    j=0
#    while (plot_time['datetime'].loc[i] <= time_aux):
#        i=i+1
#        j=j+1
#        if (i==len(plot_time.index)):
#            j=j+1
#            break
#    new_row = {'num_car':j, 'datetime':time_aux}
#    df_plot = df_plot.append(new_row, ignore_index=True)
#    
#plt.bar(df_plot.index,df_plot['num_car'])

    
    
#    plot_time['MAC'].count()
    

#plt.plot(plot_time['datetime'], plot_time['count'],marker='o')
#plt.plot(plot_time['datetime'], plot_time['count'],marker='o')
#plt.show()




#dados=[]      #vetor com todas as linhas do txt
#end=[]        #vetor com todos os endereços mac (incluem repetidos)
#tipo=[]       #vetor com todos os tipos dos dispositivos 
#rssi=[]       #vetor com todos os rssi (intensidade de sinal)
#data=[]       #vetor com todos as datas
#horas=[]      #vetor com todos as horas
#num_scans=0   #armazena número total de escaneamentos
#num_pausas=0  #armazena número de pausas no scan
#index_end=[]  #vetor com os índices da primeira aquisição de cada MAC distinto
#lista_macs=[] #vetor com os endereços MAC (excluem repetidos)
#num_macs=0    #armazena número total de macs distintos
#repete=[]     #vetor com as repetições de cada MACs
#data_on=[]    #vetor com as datas do inicio e volta dos scans
#horas_on=[]   #vetor com as horas das pausas e final do scan
#data_off=[]   #vetor com as datas das pausas e final do scan
#horas_off=[]  #vetor com as horas das pausas e final do scan
#
#
#arq = open('_TESTE_V2.TXT', 'r')
#
#dados = arq.readlines()
#for linha in dados:
#    if(linha[0]=='+'):  #para evitar lixo ou linha vazia
#        linha = linha.strip() #remove \n da linha
#        END,TIPO,RSSI,DATA,HORAS= linha.split(',')
#        end.append(END)
#        tipo.append(TIPO)
#        rssi.append(RSSI)
#        data.append(DATA)
#        horas.append(HORAS)
#    if(linha[0]=='S'):
#        if(linha[6]=='N'):
#            DATA_ON,HORAS_ON= linha.split(',')
#            DATA_ON=DATA_ON.replace("SCAN ON:  ","")
#            data_on.append(DATA_ON)
#            horas_on.append(HORAS_ON)
#        if(linha[6]=='F'):   
#            DATA_OFF,HORAS_OFF= linha.split(',')
#            DATA_OFF=DATA_OFF.replace("SCAN OFF:  ","")
#            data_off.append(DATA_OFF)
#            horas_off.append(HORAS_OFF)
#arq.close()
#
#print("\nDADOS DO ESCANEAMENTO:") 
#num_scans=len(end)
#num_pausas=len(data_on)-1
#print("Número de scans: "+str(num_scans))
##print("Começou em",data_on[0],"às",horas_on[0],end='') 
##print("Terminou em",data_off[len(data_off)-1],"às",horas_off[len(horas_off)-1],end='')
##print("Pausou:",num_pausas,"vezes") 
##for i in range(num_pausas):
##    print("Pausou em",data_off[i],"às",horas_off[i],end='')
##    print("Voltou em",data_on[i+1],"às",horas_on[i+1],end='')
#    
#
#for i in range(num_scans):
#    end[i] =end[i].replace("+INQ:","") #remove "+INQ:" dos endereços
#    #print(end[i]+","+tipo[i]+","+rssi[i]+","+data[i]+","+horas[i])
#
## Armazena somente a primeira aquisição de cada carro em "lista_macs"    
#for i in end:
#    if i not in lista_macs:
#        index_end.append(end.index(i))
#        lista_macs.append(i)
#print("\nPRIMEIRA VEZ QUE CADA MAC FOI ENCONTRADO:")  
#num_macs=len(lista_macs)
#print("Número de MACs (distintos): "+str(num_macs))       
#for i in index_end:
#    print(end[i]+" encontrado em "+data[i]+" às "+horas[i])
#
#
## Armazena quantas vezes achou cada carro em "repete"
#for i in lista_macs:
#    repete.append(end.count(i));
#print("\nREPETIÇÕES DE CADA MAC:") 
#for i in range(len(lista_macs)):    
#    print(lista_macs[i]+" foi encontrado "+str(repete[i])+" vez(es)")
# %%
