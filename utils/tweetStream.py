import os
import codecs
import pickle

from .tweet import Tweet
from .logger import getLogger
from .dataframe import TweetsDataFrameGenerator, TweetsDataFrame

log = getLogger('tw.tweet_formating', file_level='INFO')
class TweetStream(object):
    def __init__(self, filename):
        self.name = os.path.basename(filename)
        self.generator=TweetsDataFrameGenerator()
        if os.path.exists(filename):
            with codecs.open(filename, 'r', encoding='utf8') as f:
                raw_log = f.read()

            content = raw_log.split("source: spout:3, stream: default, id: {}, ")[1:]
            for i in range(len(content)):
                end_tweet_index = content[i].rfind('}}]')+3
                content[i] = content[i][:end_tweet_index]
            for t in content:
                try:
                    tw = (Tweet(t))
                    self.generator.append(tw)
                    if tw.retweetedStatus:
                        self.generator.append(tw.retweetedStatus)

                except (ValueError, IndexError) as e:
                    log.warning('Ignored : %s'%t)
                    continue
        self.df = self.generator.get_df()

    def __str__(self):
        return '%s tweets in file %s'%(self.size(), self.name)

    def size(self):
        return len(self.df)

    @classmethod
    def load(self, filename):
        self.name = filename
        stream = TweetStream('')
        stream.df = TweetsDataFrame.read_csv(filename)
        return stream
