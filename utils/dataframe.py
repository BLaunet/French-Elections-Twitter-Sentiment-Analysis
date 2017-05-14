import pandas as pd

class DataFrame(pd.DataFrame):
    _index_col = ''
    _dates = ['']

    def __init__(self, df):
        super().__init__(df)

    @classmethod
    def read_csv(cls, path, **kwargs):
        try:
            return cls(pd.read_csv(path, encoding='utf-8', index_col=cls._index_col, parse_dates=cls._dates, **kwargs))
        except:
            return cls(pd.DataFrame())

    def drop_duplicates(self, **kwargs):
        if 'keep' not in kwargs:
            kwargs['keep'] = 'last'
        if 'inplace' not in kwargs:
            kwargs['inplace'] = True
        if not 'subset' in kwargs:
            if kwargs['inplace']:
                self.__init__(self[~self.index.duplicated(keep=kwargs['keep'])])
                return None
            else:
                return self.__class__(self[~self.index.duplicated(keep=kwargs['keep'])])
        else:
            if kwargs['inplace']:
                (super().drop_duplicates(**kwargs))
                return None
            else:
                return self.__class__(super().drop_duplicates(**kwargs))

    def to_csv(self, path):
        super().to_csv(path, encoding='utf8', index_label=self._index_col)

    def info(self, **kwargs):
        if 'memory_usage' not in kwargs:
            kwargs['memory_usage'] = 'deep'
        super().info(**kwargs)
    #def memory_usage(self, **kwargs):
#        if 'deep' not in kwargs:
#            kwargs['deep'] = True
#        super().memory_usage(**kwargs)

class SummaryDataFrame(DataFrame):
    _index_col = 'fileNumber'
    _dates = ['Min_Date', 'Max_Date']
    def __init__(self, df):
        super().__init__(df)

class TweetsDataFrame(DataFrame):
    _index_col = 'createdAt'
    _dates = ['createdAt']
    def __init__(self, df):
        super().__init__(df)

    def drop_duplicates(self, **kwargs):
        if 'subset' not in kwargs:
            kwargs['subset'] = 'id'
        return super().drop_duplicates(**kwargs)

    def min_date(self):
        return self.index.min()
    def max_date(self):
        return self.index.max()
    def n_of_rt(self):
        return (self['retweetedStatus'] != 0).sum()


class DataFrameGenerator(object):
    _fields = ['']
    _main_col = ''
    _index = ''
    def __init__(self):
        for f in self._fields:
            setattr(self, f, [])

    def get_df(self):
        if getattr(self, self._main_col):
            df = pd.DataFrame(getattr(self, self._main_col), index=getattr(self, self._index), columns=[self._main_col])
            for f in self._fields:
                if f != self._index and f != self._main_col:
                    df[f] = getattr(self, f)
            return df
        else:
            return None

class SummaryDataFrameGenerator(DataFrameGenerator):
    _fields = ['fileNumber', 'Tweets', 'Retweets', 'unique', 'Min_Date', 'Max_Date']
    _main_col = 'Tweets'
    _index = 'fileNumber'
    def __init__(self):
        super().__init__()

    def append(self, fn, tweetDF):
        self.fileNumber.append(fn)
        self.Tweets.append(len(tweetDF))
        if not tweetDF.empty:
            self.Retweets.append(tweetDF.n_of_rt())
            self.Min_Date.append(tweetDF.min_date())
            self.Max_Date.append(tweetDF.max_date())
            self.unique.append(len(tweetDF.drop_duplicates(inplace=False)))
        else:
            self.Retweets.append(0)
            self.Min_Date.append(None)
            self.Max_Date.append(None)
            self.unique.append(0)

    def get_df(self):
        return SummaryDataFrame(super().get_df())


class TweetsDataFrameGenerator(DataFrameGenerator):
    _fields = ['createdAt', 'id', 'user_id', 'lang', 'favoriteCount', 'retweetCount', 'text', 'user_description', 'userMentionEntities', 'hashtagEntities', 'isTruncated',  'retweetedStatus']
    _main_col = 'id'
    _index = 'createdAt'

    def __init__(self):
        super().__init__()

    def append(self, tweet):
        user_id = tweet.user.id
        user_description = tweet.user.description.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')

        RT_id = tweet.retweetedStatus.id if tweet.retweetedStatus else 0

        for k in self._fields:
            if k == 'user_id':
                self.user_id.append(user_id)
            elif k == 'user_description':
                self.user_description.append(user_description)
            elif k == 'retweetedStatus':
                self.retweetedStatus.append(RT_id)
            elif k == 'text':
                self.text.append(tweet.text.replace('\r', ' ').replace('\n', ' ').replace('\t', ' '))
            else:
                self.__dict__[k].append(getattr(tweet,k))

    def get_df(self):
        return TweetsDataFrame(super().get_df())
