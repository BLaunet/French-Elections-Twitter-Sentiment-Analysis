
from utils import *
import os
import glob
import pickle
import pandas as pd

log = getLogger('tw.tweet_formating')

raw_dir='./tweets/'
formated_dir = './formated_tweets'

overwrite = False

file_list = glob.glob('%s/*'%raw_dir)
file_list.sort(key=lambda f: int(os.path.basename(f)))

summary_path = 'Collect_Summary.csv'
summaryTable = SummaryDataFrame.read_csv(summary_path)
summary_generator = SummaryDataFrameGenerator()
i=0
for raw_path in file_list:
    number = os.path.basename(raw_path)
    save_path = '%s/%s.csv'%(formated_dir, number)
    if number in summaryTable.index and not overwrite and os.path.exists(save_path):
        log.debug ('%s already formated'%number)
        continue
    if os.path.exists(save_path):
        TS = TweetStream.load(save_path)
    else:
        #break
        TS = TweetStream(raw_path)
        if not TS.df.empty:
            TS.df.to_csv(save_path)
    log.info('%s tweets in file %s'%(len(TS.df), number))
    summary_generator.append(number, TS.df )

    i+=1
    if i%50 == 0:
        table = summary_generator.get_df()
        summary_generator = SummaryDataFrameGenerator()
        summaryTable = pd.concat([summaryTable, table])
        summaryTable.to_csv('Collect_Summary.csv')

table = summary_generator.get_df()
summaryTable = pd.concat([summaryTable, table])
summaryTable.to_csv('Collect_Summary.csv')
