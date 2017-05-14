from utils import *
from ast import literal_eval

main_path = '.'
path = '%s/scored_270_4528_sorted.csv'%main_path
c_size = 4200000
csv_iterator = pd.read_csv(path, chunksize = c_size,encoding='utf-8', index_col='createdAt', parse_dates=['createdAt'])
i=0
while True:
    try:
        scored_chunk = TweetsDataFrame(next(csv_iterator))
        i+=1
        print(i)
        scored_chunk.drop_duplicates()
        scored_chunk['relevant_words'] = scored_chunk['relevant_words'].apply(literal_eval)
        scored_chunk.to_pickle('%s/scored_%s.df'%(main_path,i))
    except StopIteration:
        break
