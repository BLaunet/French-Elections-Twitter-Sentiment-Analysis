import pickle
import os

from .logger import getLogger
log = getLogger('tw.dict')
import random
random.seed(42)

class Dictionnary(object):
    def __init__(self, path):
        self.path = path
        self.log = getLogger('tw.dict.%s'%os.path.splitext(os.path.basename(path))[0])
        self.dict = {}
        self.buffer_threshold = 1
        self.key_buffer = []
        self.load()

    def load(self, path=None):
        if not path:
            path=self.path
        if os.path.exists(path):
            self.log.info('Loading dict at %s'%path)
            with open(path, 'rb') as f:
                while True:
                    try:
                        k,v = pickle.load(f)
                        self.dict[k] = v
                    except (EOFError):
                        break
            self.log.info('%s keys have been loaded'%len(self.dict))

    def save(self, path=None):
        if not path:
            path=self.path
        with open(path, 'wb') as f:
            for k,v in self.dict.items():
                pickle.dump([k, v],f)
    def save_buffer(self, forced=False,k_buf=None, path=None):
        if not k_buf:
            k_buf=self.key_buffer
        if forced or len(k_buf) >= self.buffer_threshold:
            if not path:
                path=self.path
            self.log.info('Saving key buffer of len %s at %s'%(len(k_buf),path))
            with open(path, 'ab') as f:
                for k in k_buf:
                    pickle.dump([k, self.dict[k]],f)
            self.key_buffer=[]

    def items(self):
        return self.dict.items()
    def values(self):
        return self.dict.values()
    def keys(self):
        return self.dict.keys()

    def __getitem__(self, k):
        return self.dict[k]
    def __setitem__(self, k, v):
        if k not in self.dict:
            self.dict[k] = v
            self.key_buffer.append(k)
            self.save_buffer()
    def __contains__(self, k):
        return k in self.dict
    def __repr__(self):
        return self.dict.__repr__()
    def __str__(self):
        return self.dict.__str__()
    def __len__(self):
        return len(self.dict)
    def __iter__(self):
        return iter(self.dict)

class WordsDictionnary(Dictionnary):
    def __init__(self, path):
        super().__init__(path)

        self.buffer_threshold = 500
        starting_dict = {}
        starting_dict['fb']='facebook'
        starting_dict['lo']='lo'
        starting_dict['yt']='youtube'
        starting_dict["'y'a"]='il y a'
        starting_dict['pb']='problème'
        starting_dict['pbs']='problèmes'
        starting_dict['tt'] = 'tout'
        starting_dict['tte'] = 'toute'
        starting_dict['ttes'] = 'toutes'
        for k,v in starting_dict.items():
            if not k in self.dict:
                self[k]=v


    def __contains__(self, k):
        return k.lower() in self.dict
    def __setitem__(self, k, v):
        k = k.lower()
        if k not in self.dict:
            self.dict[k] = v.lower()
            self.key_buffer.append(k)
            self.save_buffer()

    def __getitem__(self, k):
        v = self.dict[k.lower()]
        if k == k.upper():
            return v.upper()
        elif k == k.capitalize():
            return v.capitalize()
        else:
            return v

class TweetDictionnary(Dictionnary):
    def __init__(self, path):
        super().__init__(path)
        self.processed_files=[]
        self.buffer_threshold = 5000


    def random_tweet(self):
        if self.dict:
            return random.choice(list(self.values()))
        else:
            return None

    def update_file_list(self, filename):
        self.processed_files.append(filename)
