# -*- coding: utf-8 -*-
"""
Created on Fri Mar  9 17:25:49 2018

@author: pauline
"""
import re
import pandas as pd 
import numpy as np
import csv
import unicodedata

def remove_accents(string):
    chaine = string
    chaine = unicodedata.normalize('NFKD', string).encode('ASCII', 'ignore')
    return chaine.decode('UTF-8')
    
file='input_data/StopWords.txt'
stopwords=[line.rstrip('\n') for line in open(file)]

def keywords(string):
    words = string.split(' ')
    keywords=[]
    i=0
    while (len(keywords)<3) and (i<len(words)) :
        word=words[i].lower()
        i+=1
        token=re.sub('[^a-zA-Z]','',word)
        if token not in stopwords:
            keywords.append(token)
    while len(keywords)<3:
        keywords.append('')
    return(keywords[0],keywords[1],keywords[2])
    
#loading useful data from other sources
cities_ca=[line.rstrip('\n') for line in open('input_data/ca_cities.txt')]
provinces_ca=['Alberta','British Columbia','Prince Edward Island','Manitoba','New Brunswick','Nova Scotia','Nuvanut','Ontario','Quebec','Saskatchewan','Newfoundland and Labrador','Yukon','Northwest Territories']
codes_ca=['AB','BC','PE','MB','NB','NS','NU','ON','QC','SK','NL','YT','NT']
cities_us=[line.rstrip('\n') for line in open('input_data/us_cities.txt')]
states_us=[line.rstrip('\n') for line in open('input_data/provinces_us.txt')]
codes_us=[line.rstrip('\n') for line in open('input_data/codes_us.txt')]

def find_loc_fields(string):
    city,city_found='',False
    province=''
    country=''
    canada=''
    k=0
    while (not city_found) and (k<max(len(cities_us),len(cities_ca))-1): 
        if cities_ca[k] in string:
            city=remove_accents(cities_ca[k])
            country='Canada'
            canada='Y'
            city_found=True
        elif cities_us[k] in string:
            city=remove_accents(cities_us[k])
            country='US'
            canada='N'
            city_found=True
        k+=1
    if not city_found:
        city=remove_accents(string)

    filled=False
    for j in range (0,len(provinces_ca)):
        if provinces_ca[j] in string or codes_ca[j] in string:
            province=provinces_ca[j]
            country='Canada'
            canada='Y'
            filled=True
    if filled==False:
        if 'Canada' in string or 'canada' in string:
            country,canada='Canada','Y'
        else:
            canada='N'
            for j in range (0,len(states_us)):
                if states_us[j] in string or codes_us[j] in string.split(' '):
                    province=states_us[j]
                    country='US'
    return(city,province,country,canada)

with open('input_data/date.csv') as f1:
    date = np.array([[str(e) for e in row] for row in csv.reader(f1, delimiter=';', quoting=csv.QUOTE_NONE)])
with open('input_data/costs.csv') as f2:
    costs = np.array([[str(e) for e in row] for row in csv.reader(f2, delimiter=';', quoting=csv.QUOTE_NONE)])
with open('input_data/disaster.csv') as f3:
    disaster = np.array([[str(e) for e in row] for row in csv.reader(f3, delimiter=';', quoting=csv.QUOTE_NONE)])
with open('input_data/summary.csv') as f4:
    summary = np.array([[remove_accents(str(e)) for e in row] for row in csv.reader(f4, delimiter=';', quoting=csv.QUOTE_NONE)])
with open('input_data/dataset.csv') as f5:
    dataset = np.array([[remove_accents(str(e)) for e in row] for row in csv.reader(f5, delimiter=';', quoting=csv.QUOTE_NONE)])

n=len(dataset)
fact_table=np.empty([n,9])
#Start-Date-key | end_date_key |location_key | disaster_key |description_key | cost_key |fatalities |injured |evacuated
#summary: fill key words and save table in a new csv file
for i in range (1,len(summary)):
    a,b,c=keywords(re.sub('[^A-Za-z0-9 ]','',dataset[i][6]))
    summary[i][1]=re.sub('[^A-Za-z0-9 ]','',dataset[i][6])
    summary[i][2]=a
    summary[i][3]=b
    summary[i][4]=c
summary_filled=summary.tolist()
with open("summary_filled.csv",'w') as created:
    pass
with open("summary_filled.csv",'r+') as resultFile:
    wr = csv.writer(resultFile,delimiter=';', quoting=csv.QUOTE_ALL)
    wr.writerows(summary_filled)
#summary_filled is now saved
#TO BE DONE IN EXCEL BEFORE IMPORTING: DELETING EMPTY ROWS AND NOISE IN ADDITIONAL COLUMNS

#location dimension: fill everything while discarding duplicates and generating surrogate keys, create and save in a csv file
dic={}
surrogate_key=1

#fact table: find matching keys while scanning dataset and dimensions
for i in range(1,n):
    
    #location: filling a dico for the dimension table 
    #  + getting the location key in the fact table
    location=dataset[i][4]
    city,province,country,canada=find_loc_fields(location)
    if [city,province,country,canada] not in dic.values():
        dic[surrogate_key]=[city,province,country,canada]
        fact_table[i][2]=surrogate_key
        surrogate_key+=1
    else:
        for key in dic.keys():
            if dic.get(key)==[city,province,country,canada]:
                fact_table[i][2]=key

#copy facts
    try: #copying fatalities
        fact_table[i][6]=int(dataset[i][7])
    except:
        fact_table[i][6]=0
    try: #copying injured
        fact_table[i][7]=int(dataset[i][8])
    except:
        fact_table[i][7]=0
    try: #copying evacuated
        fact_table[i][8]=int(dataset[i][9])
    except:
        fact_table[i][8]=0

#find dates key
    start_date=dataset[i][5]
    end_date=dataset[i][12]
    start_date_key=0
    end_date_key=0
    for j in range(1,len(date)):
        if (start_date==date[j][1]):
            start_date_key=date[j][0]
            fact_table[i][0]=int(start_date_key)
        if (end_date==date[j][1]):
            end_date_key=date[j][0]
            fact_table[i][1]=int(end_date_key)
        if (start_date_key!=0) and (end_date_key!=0): #if we have found both keys
            break

#find disaster key
    category=dataset[i][0]
    group=dataset[i][1]
    subgroup=dataset[i][2]
    disaster_type=dataset[i][3]
    disaster_key=0
    for j in range(1,len(disaster)):
        if category==disaster[j][1] and group==disaster[j][2] and subgroup==disaster[j][3] and disaster_type==disaster[j][4]:
            disaster_key=disaster[j][0]
            fact_table[i][3]=int(disaster_key)
            break
#find description key
    comment=re.sub('[^A-Za-z0-9 ]','',dataset[i][6])
    description_key=0
    for j in range(1,len(summary)):
        if comment==summary[j][1]:
            description_key=summary[j][0]
            fact_table[i][4]=int(description_key)
            break

#find costs key
    c1=dataset[i][10]
    c2=dataset[i][11]
    c3=dataset[i][13]
    c4=dataset[i][14]
    c5=dataset[i][15]
    c6=dataset[i][16]
    c7=dataset[i][17]
    c8=dataset[i][18]
    c9=dataset[i][19]
    costs_key=0
    for j in range(1,len(costs)):
        if c1==costs[j][1] and c2==costs[j][2] and c3==costs[j][3] and c4==costs[j][4] and c5==costs[j][5] and c6==costs[j][6] and c7==costs[j][7] and c8==costs[j][8] and c9==costs[j][9]:
            costs_key=costs[j][0]
            fact_table[i][5]=int(costs_key)
            break
fact_table=fact_table.astype(int)
df = pd.DataFrame(fact_table)
df.to_csv("fact_table.csv") 
#first column and first row to be deleted in the dsv files
#(indexes of the matrix not needed)
location_filled=["" for i in range(0,len(dic.values())+1)]
location_filled[0]=['ID','City','Province','Country','Canada']
for key in dic.keys():
    value=dic.get(key)
    a,b,c,d=value[0],value[1],value[2],value[3]
    location_filled[key]=[key,a,b,c,d]
with open("location_filled.csv",'w') as created:
    pass
with open("location_filled.csv",'r+') as resultFile:
    wr = csv.writer(resultFile,delimiter=';', quoting=csv.QUOTE_ALL)
    wr.writerows(location_filled)