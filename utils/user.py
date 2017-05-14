import datetime

from .logger import getLogger

log = getLogger('tw.tweet_formating.user', file_level='INFO')
class User(object):
    all_fields = ['id=', 'name=', 'screenName=', 'location=', 'description=', 'isContributorsEnabled=', 'profileImageUrl=', 'profileImageUrlHttps=', 'isDefaultProfileImage=', 'url=', 'isProtected=', 'followersCount=', 'status=', 'profileBackgroundColor=', 'profileTextColor=', 'profileLinkColor=', 'profileSidebarFillColor=', 'profileSidebarBorderColor=', 'profileUseBackgroundImage=', 'isDefaultProfile=', 'showAllInlineMedia=', 'friendsCount=', 'createdAt=', 'favouritesCount=', 'utcOffset=', 'timeZone=', 'profileBackgroundImageUrl=', 'profileBackgroundImageUrlHttps=', 'profileBackgroundTiled=', 'lang=', 'statusesCount=', 'isGeoEnabled=', 'isVerified=', 'translator=', 'listedCount=', 'isFollowRequestSent=']

    fields = ['id=', 'description=']
    def __init__(self, string):
        log.debug('USER')
        for f in User.fields:
            index_begin = string.find(f)+len(f)
            index_max = string.find(User.all_fields[User.all_fields.index(f)+1], index_begin)-2
            if f == 'id=':
                try:
                    attr = int(string[index_begin:index_max])
                except ValueError as e:
                    attr = None
                    raise
            elif f in ['isGeoEnabled=', 'isVerified=', 'isProtected=', 'translator=', 'showAllInlineMedia=']:
                if string[index_begin:index_max] == 'true':
                    attr = True
                elif string[index_begin:index_max] == 'false':
                    attr = False
                else:
                    print('Unable to determine the value of %s for field %s'%(string[index_begin:index_max],f))
            elif f in ['name=', 'screenName=', 'location=', 'description=', 'timeZone=', 'lang=']:
                attr = string[index_begin+1:index_max-1].replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            elif f == 'createdAt=':
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                cDate = string[index_begin:index_max].split(' ')
                try:
                    time = list(map(int,cDate[3].split(':')))
                except IndexError as e:
                    print(cDate)
                    raise
                attr = datetime.datetime(month=months.index(cDate[1])+1, day=int(cDate[2]), year = int(cDate[5]), hour=time[0], minute=time[1], second=time[2])
            else:
                attr = (string[index_begin:index_max])
            setattr(self, f[:-1],attr)
            log.debug('%s set to %s'%(f[:-1],attr))



    def __str__(self):
        return '{'+', '.join(['%s = %s'%(f, getattr(self, f)) for f in vars(self)])+'}'

    def __repr__(self):
        return self.name
    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.id == other.id
    def __ne__(self, other):
        """Define a non-equality test"""
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
    def __hash__(self):
        """Override the default hash behavior (that returns the id or the object)"""
        return hash(tuple(sorted(self.__str__())))
