########################################################
#################### Global Vars #######################
########################################################

# this is the environment,whether you test on local
#   machine or run on HPC dataset
ENV = 'test'

# use this value as a threshold which fields to keep
#    based on MAG certainty, currently as long as MAG
#    is >50% certain of some field -- we count it
FIELD_CONFIDENCE = 0.5

import time
START_TIME = time.monotonic()
########################################################
###################### Imports #########################
########################################################

import pandas as pd
import numpy as np
from scipy import stats
from ast import literal_eval
from io import StringIO
import itertools
import sys
from datetime import datetime
from sklearn.preprocessing import StandardScaler

########################################################
####################### Paths ##########################
########################################################

if ENV == 'HPC':
    path = "/scratch/aal544/"
    mag = "/MAG_2021/"

if ENV == 'test':
    path = "../data/"
    mag = "mag/"

########################################################
########### Get the Paper-Field associations ###########
########################################################

# read in the data
PaperMetrics = pd.read_csv(path+mag+"PaperFieldsOfStudy.txt", sep='\t', header = None)
PaperMetrics.columns = ['PID', 'PaperFields', 'confidence']

# only keep the fields that we are FIELD_CONFIDENCE certain in and drop confidence since we don't need it anymore
PaperMetrics = PaperMetrics[PaperMetrics['confidence'] > FIELD_CONFIDENCE].drop('confidence', axis = 'columns')

# group by PID and keep all fields in the set of fields per paper
PaperMetrics = PaperMetrics.groupby(by = 'PID').agg(set).reset_index()

sys.stdout.write('Got papers and the fields ' + str(time.monotonic()  - START_TIME)+ '\n')
sys.stdout.flush()

########################################################
########### Get the Paper Publication Years ############
########################################################

# get the Papers and get the publication years for each paper
PaperPubYear = pd.read_csv(path+mag+'Papers.txt', sep = '\t', header= None, usecols=[0,7], dtype={7:str}).dropna()
PaperPubYear.columns = ['PID', 'PubYear']


def cast_year_to_int(y):
    '''
        paper publication year is of a funky
        format so I created this simple function
        to purify the year and keep it as int
    '''
    y = str(y)
    y = y.replace("'","")
    y = y.replace("\"","")
    try:
        val = int(str(y)[:4])
    except:
        val = 9999
    return val

# cast year to int
PaperPubYear['PubYear'] = PaperPubYear['PubYear'].apply(cast_year_to_int)

# merge all papers by years
PaperMetrics = pd.merge(PaperMetrics, PaperPubYear, on = 'PID').sort_values(by=['PubYear'])

sys.stdout.write('Sorted the papers by year ' + str(time.monotonic()  - START_TIME)+ '\n')
sys.stdout.flush()

########################################################
######## Extend Fields with the Parent Fields  #########
########################################################

# these are kept (FieldID : ChildID)
FieldOfStudyChildren= pd.read_csv(path + mag + 'FieldOfStudyChildren.txt', sep = '\t', header= None)

cnt = 0
FOStree = {}

for index, row in FieldOfStudyChildren.iterrows():
    '''
        Generate (ChildID : {Parent1, Parent2}) sets
    '''
    if row[1] not in FOStree:
            FOStree[row[1]] = set()
    FOStree[row[1]].add(row[0])


def get_parents(low_lvl_fields):
    '''
        simple BFS search applied on graph
        to propagate nodes up and get all parent
        nodes
    '''
    seen = set()
    queue = list(low_lvl_fields)
    global cnt
    if cnt %10**7 == 0:
            sys.stdout.write('Got parent fields for '+ str(cnt)+ ' || seconds: '+ str(time.monotonic() - START_TIME) +'\n')
            sys.stdout.flush()
    cnt+=1
    while queue:
            elem =queue.pop()
            if elem not in seen:
                    seen.add(elem)
                    if elem in FOStree:
                                    queue.extend(
                                            FOStree[elem]
                                    )
    return seen

PaperMetrics["PaperFields"] = PaperMetrics["PaperFields"].apply(get_parents)

sys.stdout.write('Got all of the field parent nodes ' + str(time.monotonic()  - START_TIME)+ '\n')
sys.stdout.flush()
########################################################
############## Count Fields per Level  #################
########################################################

fos_levels = pd.read_csv(path + mag +'FieldsOfStudy.txt', sep = '\t', header= None, usecols=[0,5])

sys.stdout.write("Read In Fields and Sets, converting to a dict\n")
sys.stdout.flush()


lev = {}
for index, row in fos_levels.iterrows():
        lev[row[0]] = row[5]


cnt = 0
def get_levels(fields):
        ans = [0,0,0,0,0,0]
        global cnt
        if cnt %(35*10**6) == 0:
                sys.stdout.write('Got level counts for '+ str(cnt)+ ' || seconds: '+ str(time.monotonic() - START_TIME) +'\n')
                sys.stdout.flush()
        cnt+=1

        for i in fields:
                ans[lev[i]]+=1
        return ans


PaperMetrics['LevelCounts'] = PaperMetrics['PaperFields'].apply(get_levels)

sys.stdout.write('Computed the level counts for papers ' + str(time.monotonic()  - START_TIME)+ '\n')

sys.stdout.flush()

########################################################
############## Calculate Talal's Metric  ###############
########################################################

# we will keep look for how many unique field pairs
# each paper introduces in relation to all 2-combinations
# for all other fields that were published together


current_year = 0
duple_occurence_curr = set()
duple_occurence_prev = set()

records_for_papers = {}
cnt = 0
for i in zip(*PaperMetrics[['PID', 'PaperFields','PubYear']].to_dict("list").values()):
    if current_year!=i[-1]:
        current_year = i[-1]
        duple_occurence_prev = duple_occurence_curr.copy()

    tp = i[1]
    introduced_tuple = 0

    for tup in itertools.combinations(tp, 2):
        tup = tuple(sorted(tup))
        if tup not in duple_occurence_curr:
            duple_occurence_curr.add(tup)
        if (not duple_occurence_prev) or (tup not in duple_occurence_prev):
            introduced_tuple+=1

    if len(tp) == 1: introduced_tuple=-1
    records_for_papers[i[0]] = (introduced_tuple, len(tp))
    if cnt%(10**7)==0:
        sys.stdout.write('completed: ' + str(cnt) + '\n')
        sys.stdout.write('time spent ' + str(time.monotonic()  - START_TIME)+ '\n')
        sys.stdout.flush()
    cnt+=1

tuple_counts_df = pd.DataFrame.from_dict(records_for_papers, orient='index')
tuple_counts_df = tuple_counts_df.reset_index()
tuple_counts_df.columns = ['PID', 'New_Tuples','Field_Count']

PaperMetrics = pd.merge(PaperMetrics,tuple_counts_df, on = 'PID' )

sys.stdout.write('Computed Talals Metric ' + str(time.monotonic()  - START_TIME)+ '\n')
sys.stdout.flush()

########################################################
########## Get Depth and Interdisciplinarity  ##########
########################################################

# just get the max index of non 0 value in levels
# this is how deep the researchers went
PaperMetrics['Depth'] = PaperMetrics['LevelCounts'].apply(lambda x:np.max(np.where(x)) )

# here is one possible way to use New_Tuples and All Tuples
# df['metric'] = df['new_tuples'] / df['cnt_fields']

PaperMetrics['lvl0'] = PaperMetrics['LevelCounts'].apply(lambda x: x[0])
PaperMetrics['lvl1'] = PaperMetrics['LevelCounts'].apply(lambda x: x[1])
PaperMetrics['lvl2'] = PaperMetrics['LevelCounts'].apply(lambda x: x[2])
PaperMetrics['lvl3'] = PaperMetrics['LevelCounts'].apply(lambda x: x[3])
PaperMetrics['lvl4'] = PaperMetrics['LevelCounts'].apply(lambda x: x[4])
PaperMetrics['lvl5'] = PaperMetrics['LevelCounts'].apply(lambda x: x[5])

# since we are dealing with a vector [x0,x1,x2...x5]
# it's a reasonable statement to say that higher x0 automatically
# makes the paper more Interdisciplinary than high x1
# hence let's first aggregate all values by multiplying and preserving the > relation
# and then scale it with Standard Scaler
SCALE_FACTOR = 57
PaperMetrics['Interdisciplinarity'] = SCALE_FACTOR*(SCALE_FACTOR*(SCALE_FACTOR*(SCALE_FACTOR*(SCALE_FACTOR*PaperMetrics['lvl0']+PaperMetrics['lvl1'])+PaperMetrics['lvl2'])+PaperMetrics['lvl3'])+PaperMetrics['lvl4'])+PaperMetrics['lvl5']

scaler = StandardScaler()
PaperMetrics[["Interdisciplinarity"]] = scaler.fit_transform(PaperMetrics[["Interdisciplinarity"]])

PaperMetrics = PaperMetrics.drop(['lvl0', 'lvl1', 'lvl2', 'lvl3', 'lvl4', 'lvl5'], axis = 'columns')

sys.stdout.write('Computed All Metrics, saving... ' + str(time.monotonic()  - START_TIME)+ '\n')
sys.stdout.flush()

########################################################
################## Save the Metrics  ###################
########################################################

PaperMetrics.to_csv(path+'/FinalWriteUp.csv', index = False)

sys.stdout.write('Metrics File Written to Disk. ' + str(time.monotonic()  - START_TIME)+ '\n')
sys.stdout.flush()