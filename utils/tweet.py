import datetime
import re

from .user import User
from .userMention import UserMention
from .logger import getLogger

log = getLogger('tw.tweet_formating.tweet', file_level ='INFO')

class Tweet(object):
    all_fields = ['createdAt=', 'id=', 'text=', 'source=', 'isTruncated=', 'inReplyToStatusId=','inReplyToUserId=', 'isFavorited=', 'isRetweeted=', 'favoriteCount=', 'inReplyToScreenName=', 'geoLocation=', 'place=', 'retweetCount=', 'isPossiblySensitive=', 'lang=', 'contributorsIDs=', 'retweetedStatus=', 'userMentionEntities=', 'urlEntities=', 'hashtagEntities=', 'mediaEntities=', 'symbolEntities=', 'currentUserRetweetId=', 'user=']

    fields = ['createdAt=', 'id=', 'text=', 'isTruncated=', 'favoriteCount=', 'retweetCount=', 'lang=', 'retweetedStatus=', 'userMentionEntities=', 'hashtagEntities=', 'user=']
    def __init__(self, str):
        i = 0
        log.debug('TWEET')
        for f in Tweet.fields:
            if Tweet.all_fields.index(f) <= Tweet.all_fields.index('retweetedStatus='):
                index_begin = str.find(f, i)+len(f)

                if f == "retweetedStatus=":
                    index_max = str.rfind("userMentionEntities=")-2
                    if(str.rfind("userMentionEntities=")!= str.find("userMentionEntities=")):
                        attr = Tweet(str[index_begin:index_max])
                    else:
                        attr = None
                else:
                    index_max = str.find(Tweet.all_fields[Tweet.all_fields.index(f)+1], i)-2
                    if f == 'text=':
                        attr = str[index_begin:index_max]
                        matches = re.finditer(r"\n", attr)
                        for m_num, m in enumerate(matches):
                            attr = attr[:m.start()]+' '+attr[m.end():]
                    elif f =='createdAt=':
                        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                        cDate = str[index_begin:index_max].split(' ')
                        time = list(map(int,cDate[3].split(':')))
                        attr = datetime.datetime(month=months.index(cDate[1])+1, day=int(cDate[2]), year = int(cDate[5]), hour=time[0], minute=time[1], second=time[2])
                    else:
                        attr = str[index_begin:index_max]

            else:
                index_begin = str.find(f,i)+len(f)
                if f == 'user=':
                    index_max = str.rfind('}}')+1
                    try:
                        attr = (User(str[index_begin:index_max]))
                    except (ValueError, IndexError) as e:
                        log.warning('Impossible to create User object from '+str[index_begin:index_max])
                        attr = None
                        raise

                else:
                    index_max = str.rfind(Tweet.all_fields[Tweet.all_fields.index(f)+1])-2
                    if Tweet.all_fields[Tweet.all_fields.index(f)+1] == 'user=':
                        while str[index_max:index_max+2] != ', ':
                            index_max = str[:index_max].rfind(Tweet.all_fields[Tweet.all_fields.index(f)+1])-2
                    if f == 'hashtagEntities=':
                        h = str[index_begin+1:index_max-1].replace("HashtagEntityJSONImpl{text='", '').replace("'}", '').replace("'",'').replace(' ','')
                        attr = h.split(',')
                    elif f == 'userMentionEntities=':
                        sub = str[index_begin+1:index_max-1].split('UserMentionEntityJSONImpl')[1:]
                        attr = []
                        try:
                            for s in sub:
                                attr.append((UserMention(s).screenName))
                        except ValueError as e:
                            log.warning('Impossible to create UserMention objects from '+sub)
                            raise
                    else:
                        attr = str[index_begin:index_max]
            i = index_max
            if f in ['text=', 'lang=', 'source=', '']:
                attr = attr[1:-1].replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            if f == 'lang=':
                if attr == 'fr':
                    attr = True
                else:
                    attr = False
            if f in ["id=", "favoriteCount=", "retweetCount="]:
                try:
                    attr = int(attr)
                except ValueError as e:
                    log.warning('Impossible to define %s from %s'%(f[:-1],attr))
                    attr = None
                    raise
            if f in ['isRetweeted=', 'isTruncated=', 'isFavorited=', 'isPossiblySensitive=']:
                if attr == 'false':
                    attr = False
                else:
                    attr = True
            setattr(self, f[:-1], attr)
            log.debug('%s set to %s'%(f[:-1], attr))
        self.isRetweet = self.retweetedStatus is not None

    def __str__(self):
        return '\n'.join(['%s = %s'%(f, getattr(self, f)) if (f != 'retweetedStatus' or getattr(self, 'retweetedStatus') == None) else '%s = \n\t%s'%(f, (getattr(self, f).__str__().replace('\n', '\n\t'))) for f in vars(self)])

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.id == other.id
            #return self.__dict__ == other.__dict__
        return NotImplemented
    def __ne__(self, other):
        """Define a non-equality test"""
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented
    def __hash__(self):
        """Override the default hash behavior (that returns the id or the object)"""
        return hash(tuple(self.id))
