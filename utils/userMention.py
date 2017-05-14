from .user import User
from .logger import getLogger

log = getLogger('tw.tweet_formating.userMention', file_level = 'INFO')
class UserMention(User):
    all_fields = ['name=', 'screenName=', 'id=']
    fields = ['screenName=']
    def __init__(self, str):
        log.debug('USERMENTION')
        for f in UserMention.fields:
            index_begin = str.find(f)+len(f)+1
            if f == 'id=':
                index_max = str.rfind('}')-1
                try:
                    attr = (str[index_begin:index_max])
                except ValueError as e:
                    attr = None
                    log.warning('Unable to parse id from %s'%(str[index_begin:index_max]))
                    raise
            else:
                index_max = str.find(UserMention.all_fields[UserMention.all_fields.index(f)+1])-3
                attr = str[index_begin:index_max]
            setattr(self, f[:-1],attr)
            log.debug('%s set to %s'%(f[:-1],attr))
    def __str__(self):
        return self.screenName

    def __repr__(self):
        return self.screenName
