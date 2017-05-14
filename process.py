import os
import glob
from utils import *
def propagate_candidates(group, candidates):
    rt_id = group.iloc[0,-1]
    if rt_id == 0:
        group['candidate_ref'] = candidates
    else:
        group['candidate_ref'] = pd.Series([candidates.loc[rt_id].item()]*len(group),  index=group.index)
    return group

def propagate_score(group, scored):
    if group.loc[group.first_valid_index(), 'retweetedStatus'] == 0:
        out = group.filter(['createdAt', 'id', 'user_id', 'favoriteCount', 'retweetCount']).join(scored)#[['relevant_words', 'score_neg', 'score_pos']]
    else:
        retweet_id = group.loc[group.first_valid_index(), 'retweetedStatus']
        if retweet_id in scored.index:
            out = group.filter(['createdAt', 'id', 'user_id', 'favoriteCount', 'retweetCount']).join(pd.DataFrame([scores.loc[retweet_id]]*len(group), index=group.index))
    return out

p = Tweet_Processor()
dir = './concat_dataframe/'
files = glob.glob('%s/*.csv'%dir)
files.sort(key = lambda x: int(os.path.basename(x).split('_')[2]))

for f in files:
    table = TweetsDataFrame.read_csv(f)

    table = TweetsDataFrame(table[table['lang']])
    _ = table.pop('lang')
    table.reset_index(inplace=True)
    table.index=table['id']

    cand_ref = table[table['retweetedStatus'] == 0].apply(p.candidate_reference, axis=1)
    candidates_found = table.groupby('retweetedStatus').apply(lambda x: propagate_candidates(x, cand_ref))
    candidates_found = candidates_found[~pd.isnull(candidates_found['candidate_ref'])]

    scores = candidates_found[candidates_found['retweetedStatus'] == 0].apply(p.process, axis=1)
    table_scored = candidates_found.groupby('retweetedStatus').apply(lambda x: propagate_score(x, scores))

    table_scored.index = table_scored['createdAt']
    _ = table_scored.pop('createdAt')
    scoreDataFrame = TweetsDataFrame(table_scored)

    min_i = os.path.basename(f).split('_')[2]
    max_i = os.path.basename(f).split('_')[3].replace('.csv', '')
    scoreDataFrame.to_csv('./scored_tweets/scored_tweets_%s_%s.csv'%(min_i, max_i))
