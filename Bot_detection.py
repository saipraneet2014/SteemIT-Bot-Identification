from urlextract import URLExtract
import pandas as pd
import numpy as np
import natsort
from datetime import datetime
import os

#%%
path ="/shares/dutta_gpu/steemit/data/Value-transfer-Operation-Dataset/transfer"
os.chdir(path)
extension = 'csv'
all_filenames = os.listdir(path)
actualfilepath = []
all_filenames=natsort.natsorted(all_filenames,reverse=False)


#%%
for i in all_filenames:
    if i.endswith('.csv'):
        actualfilepath.append(path + '/' + i)
    else:
        continue
    
#%%

def contains(memo, frm):
        if str(memo).__contains__(str(frm)):
            return memo
        else:
            return 'false'

transfer_memo_list=[]

for i in range(1,46):
    transfer='/shares/dutta_gpu/steemit/data/Value-transfer-Operation-Dataset/transfer/transfer-month-'+ str(i) +'.csv'
    
    vote="/shares/dutta_gpu/steemit/data/Social-network-operation-dataset/vote/vote-month-"+str(i)+".csv"    
    
    df = pd.read_csv(transfer, usecols = ['block_no','from','to','amount','memo'], index_col=None,header = 0, low_memory=False)
    df_v = pd.read_csv(vote, index_col=None,header = 0, low_memory=False)
    
    #####Transfer#####
    
    start_time = datetime.now()
            
    extractor = URLExtract()
    
    df['memo'] = df['memo'].apply(lambda x: extractor.find_urls(str(x)))
    
    df['memo'] = df.apply(lambda y: contains(y["memo"],y["from"] ),axis=1)
    
    df=df[df.memo!='false']
    
    transfer_grpby = df.groupby(['from','to'])['to'].count().reset_index(name='transfercount').rename(columns={'to' : 'voter', 'from' : 'author'})

        
    end_time = datetime.now()
    
    #####Votes#####

    vote_grpby = df_v.groupby(['author','voter'])['voter'].count().reset_index(name='votercount')
     
    mergedDF = vote_grpby.merge(transfer_grpby).loc[:,['author','voter','votercount', 'transfercount']]
    sortedDF = mergedDF.sort_values(by=['votercount','transfercount'] ,ascending=False)
    sortedDF[['votercount','transfercount']] = sortedDF[['votercount', 'transfercount']].astype(int)
    sortedDF['low_value'] = np.where(sortedDF.votercount == sortedDF.transfercount, 'True', 'False')
    rslt_df = sortedDF[sortedDF['low_value'] == 'True']

    transfer_memo_list.append(rslt_df)


#%%
i=1
for d in transfer_memo_list:
    filename = "result["+str(i)+"]"
    d['Voter_link'] = ''
    d['Voter_link'] = d['voter'].apply(lambda z: "https://steemit.com/@"+str(z))

    d.to_csv(r'/home/a/ageereddy/praneetIS/Result_DF/'+filename+'.csv', index = False,columns=['author','voter','votercount','Voter_link'], header= ['Author','Voter','Count','Voter_link'])
    i+=1
#%%
final_list=[]
author=[]
voter = []
final_df = pd.DataFrame(columns = ['User', 'Link'])

for i in range(1,45):

    df_read = pd.DataFrame()
    
    
    result='/home/a/ageereddy/praneetIS/Result_DF/result['+ str(i) +'].csv'
    df_read = pd.read_csv(result, usecols = ['Author','Voter','Count','Voter_link'], index_col=None,header = 0, low_memory=False)
    
    author.extend(df_read['Author'].unique().tolist())
    voter.extend(df_read['Voter'].unique().tolist())


#final_df = pd.DataFrame(columns = ['User', 'Link'])
final_df['User']=list(set(author+voter))
final_df['Link'] = final_df['User'].apply(lambda z: "https://steemit.com/@"+str(z))

final_df.to_csv(r'/home/a/ageereddy/praneetIS/Result_DF/Bot_list.csv', index = False,columns=['User', 'Link'], header= ['User', 'Link'])

    
