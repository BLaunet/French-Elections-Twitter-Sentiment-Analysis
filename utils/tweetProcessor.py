import hunspell
import urllib
import treetaggerwrapper
import bs4 as BeautifulSoup
import pandas as pd
import emoji
import regex as re
import time
from http.client import RemoteDisconnected, IncompleteRead
import pickle
import itertools
import os
from ast import literal_eval

from .candidate import Candidate
from .logger import getLogger
from .constants import CANDIDATES_1ST_ROUND, CANDIDATES_2ND_ROUND, FIRST_ROUND
from .dictionnary import WordsDictionnary

log = getLogger('tw.process', file_level = 'INFO', stream_level = 'WARNING')
class Tweet_Processor():

    '''

    This class implements a text processor
    It defines a bunch of useful objects and methods for tweet sentiment analysis

    '''
    def __init__(self):
        self._TreeTagger_dir = './TreeTagger/'
        self._Hunspell_dic = './Hunspell/fr-toutesvariantes.dic'
        self._Hunspell_aff = './Hunspell/fr-toutesvariantes.aff'

        self._tagger = treetaggerwrapper.TreeTagger(TAGLANG='fr', TAGDIR=self._TreeTagger_dir)
        self._speller = hunspell.HunSpell(self._Hunspell_dic, self._Hunspell_aff)

        self._expressions_csv = './Lexicons/Expressions_Complete.csv'
        self._expressions_dict = pd.read_csv(self._expressions_csv, encoding='utf-8')
        #_expr_pattern = re.compile(r'\b(?:%s)\b' % '|'.join(_expressions_dict['phrase'].tolist()), re.IGNORECASE)
        self._expr_pattern = re.compile(r"\b\L<words>\b", re.IGNORECASE, words=self._expressions_dict['phrase'].tolist())

        self._words_csv = './Lexicons/Words_Complete.csv'
        self._words_dict = pd.read_csv(self._words_csv, encoding='utf-8')
        self._words_dict['word'] = self._words_dict['word'].str.lower()
        self._words_pattern = re.compile(re.compile(r"\b\L<words>\b", re.IGNORECASE, words=self._words_dict['word'].tolist()))

        self._emoji_pattern = emoji.get_emoji_regexp()

        self._corrections_dictionary_path = './utils/corrections_dict.pkl'
        self._corrections_dict = WordsDictionnary(self._corrections_dictionary_path)

        self._typos =   [['e', 'é', 'è', 'ê'],\
                        ['a', 'à', 'â'],\
                        ['u', 'ù', 'û'],\
                        ['o', 'ô'],\
                        ['i', 'ï', 'î'],\
                        ['l', 'll'],\
                        ['t', 'tt'],\
                        ['p', 'pp'],\
                        ['r', 'rr'],\
                        ['ue', 'eu'],\
                        ['c', 'ç']]

    def process(self, tweet):
        '''
        Analyze a tweet: it filters some information and get the candidate reference and the score
        :param tweet: Tweet to score
        :type tweet: Tweet object
        :return: processed tweet
        :rtype: ProcessedTweet
        '''
        log.info('Processing tweet : %s'%tweet['id'])
        log.info('Text = %s'%tweet['text'])
        #cand_ref = self.get_candidate_reference(tweet)
        no_hashtags = self.remove_user_mentions_hashtags(tweet)
        no_emojis = self.remove_emojis(no_hashtags)
        no_candidates = self.remove_candidates_names(no_emojis)
        repl_spec_char = self.replace_special_chars(no_candidates)
        log.info('Before tokenization : %s'%repl_spec_char)
        tokens = self.tag(repl_spec_char)[0]
        log.debug('Tokens : %s'%tokens)
        words_only = self.filter_words_only(tokens)
        log.debug('Words only : %s'%words_only)

        tries = 0
        while(True):
            try:
                corrected = self.correct(words_only)
            except (RemoteDisconnected, IncompleteRead):
                tries+=1
                log.warning('Remote Disconnected. Attempts = %s'%tries)
                if tries < 4:
                    time.sleep(5)
                    continue
                else:
                    log.error('Correction failed 3 times in a row')
            break
        corrected = words_only
        log.info('Corrected : %s'%corrected)
        categories, lemmas = self.tag(' '.join(corrected))[1:]
        log.debug('Lemmas : %s'%lemmas)

        scores = self.score(' '.join(lemmas))
        log.info('Score : %s'%scores)
        relevant_words = self.find_relevant_words(categories, lemmas)
        log.info('Relevant words : %s'%relevant_words)

        out = dict()
        out['score_pos'] = scores['pos']
        out['score_neg'] = scores['neg']
        out['relevant_words'] = relevant_words + (literal_eval(tweet['hashtagEntities']))
        return tweet[['candidate_ref']].append(pd.Series(out))

    def remove_user_mentions_hashtags(self, tweet):
        '''
        Removes the user mentions and hashtags from the text of a tweet
        :param tweet: tweet to treat
        :type tweet: Tweet object
        :return: text without user mentions and hashtags
        '''
        text = tweet['text']
        if not pd.isnull(tweet['userMentionEntities']):
            userMentionEntities = literal_eval(tweet['userMentionEntities'])
            for userMention in userMentionEntities:
                text = text.replace('@%s'%userMention, '')
        if not pd.isnull(tweet['hashtagEntities']):
            hashtags = literal_eval(tweet['hashtagEntities'])
            for h in hashtags:
                text = text.replace('#%s'%h, ' ')
        return text
    def find_relevant_words(self,category, words):
        if len(category) != len(words):
            log.error('Not the same number in %s and %s'%(category, words))
            return None
        relevant_words = []
        for i in range(len(category)):
            if 'ADJ' in category[i] or 'NAM' in category[i] or 'NOM' in category[i]:
                if len(words[i]) > 2:
                    log.debug('Category found : %s'%category[i])
                    log.debug('Appending word : "%s"'%words[i])
                    relevant_words.append(words[i])
        return relevant_words

    def filter_words_only(self, list_str):
        '''
        Filter only the words in a list of strings

        It also excludes 'RT' and 'url-remplacée'

        :param list_str: list of strings
        :type list_str: list(str)
        :return: A list containing only the words
        :rtype: list(str)

        '''
        corrected_list = []
        for string in list_str:
            word = self.is_word(string)
            if not word or string=='RT' or string=='url-remplacée':
                log.debug('Removing %s'%string)
                continue
            else:
                corrected_list.append(word)
        return corrected_list

    def replace_special_chars(self, text):
        text = text.replace('’', "'")
        text = text.replace(' ️', '')
        return text
    def translate_online(self,text):
        '''
        This function uses the website http://www.traducteur-sms.com/
        to translate SMS-like text into proper French

        :param text: the text to be translated
        :type text: str

        :return: the corrected text outputed by the website
        :rtype: str
        '''

        website = 'http://www.traducteur-sms.com/?q='
        request = website+urllib.parse.quote_plus(text, encoding='latin1')
        try:
            html = urllib.request.urlopen(request).read()
        except urllib.error.URLError:
            log.warning('URL Request failed')
            return text
        soup = BeautifulSoup.BeautifulSoup(html, 'html5lib')
        try:
            correction = soup.find('div',attrs={"id":u"TEXT"}).string.strip()
        except AttributeError:
            log.warning('Could not find text in soup = %s'%soup)
            correction = ''

        if not self._speller.spell(correction):
            #We re-correct the modified k-->c
            o = text.lower()
            c = correction.lower()

            diffs = [a != b for a,b in zip(o,c)]
            for i in range(len(diffs)):
                if diffs[i]:
                    if o[i] == 'k' and c[i] == 'c':
                        c = c[:i]+'k'+c[i+1:]
            correction = c
        return correction.lower()

    def is_word(self, string):
        '''
        Check if the string is a word (starting with letter or number)

        :param string: the string to test
        :type string: str
        :return: True if string is a word
        :rtype: convertible to bool
        '''

        o = string
        #If it's a number, we remove
        if string[0].isdigit():
            return None
        try:
            while not string[0].isalpha():
                string = string[1:]
            while not string[-1].isalpha() and string[-1] not in "'":
                string = string[:-1]
        except IndexError:
            return None

        if o!=string:
            log.info('Transforming word %s --> %s'%(o, string))
        return string

    def tag(self, text):
        '''
        Decompose a text in 'tags' according to TreeTagger
        It returns 3 lists : one for token, one for category, one for lemma

        :param text: Text to tag
        :type text: str
        :return: list of tags
        :rtype: list(list(str)) dim = 3x(n_of_tokens)

        '''
        tags = self._tagger.tag_text(text)
        tokens=[]
        categories=[]
        lemmas=[]
        for t in tags:
            list = (t.split('\t'))
            if len(list)>1:
                tokens.append(list[0])
                categories.append(list[1])
                lemmas.append(list[2])
        return [tokens, categories, lemmas]

    def candidate_reference(self,tweet):
        '''
        Get a list of candidates the tweet is refering to

        :param tweet: the tweet to consider
        :type tweet: Tweet object
        :return : list of candidates
        :rtype: list(Candidate)

        '''
        found_candidates = set()
        if tweet['createdAt'] > FIRST_ROUND:
            candidates_list = CANDIDATES_2ND_ROUND
        else:
            candidates_list = CANDIDATES_1ST_ROUND
        for cand in candidates_list:
            if cand.regex().search(tweet['text']):
                found_candidates.add(cand.name)
                log.debug('Found candidate %s'%cand.name)
        #If we found nothing in the text, we look in the description
        if not found_candidates:
            if not pd.isnull(tweet['user_description']):
                if cand.regex().search(tweet['user_description']):
                    found_candidates.add(cand.name)
                    log.debug('Found candidate %s in user description'%cand.name)
        if not found_candidates:
            return pd.Series({'candidate_ref': None})
        else:
            if len(found_candidates) > 1:
               return pd.Series({'candidate_ref': None})
            else:
                return pd.Series({'candidate_ref': list(found_candidates)})

    def correct(self, words):
        '''
        Correct the words misspelled using the online corrector
        '''
        for w in words:
            if not self.is_correctly_spelled(w):
                if w not in self._corrections_dict:
                    typo = self.typo_correction(w.lower())
                    if typo:
                        correction = typo
                        log.debug('Typo correction for "%s" --> "%s"'%(w.lower(), correction))
                    else:
                        try:
                            correction = self.translate_online(w.lower())
                            log.debug('SMS correction for "%s" --> "%s"'%(w.lower(),correction))
                        except UnicodeEncodeError:
                            log.error("Unicode Error in '%s' :\t\n can't encode '%s'"%(' '.join(words), w))
                            continue
                    self._corrections_dict[w] = correction
                    log.debug('Saved in corrections dictionnary')
                else:
                    log.debug('"%s" was already corrected once'%(w))

                words[words.index(w)] = self._corrections_dict[w]
                log.info('Correction : "%s" ==> "%s"'%(w,self._corrections_dict[w]))

        return words

    def _delete_triplicates(self,s):
        '''
        Used in Typo correction if a letter is duplicated too many times
        to avoid too big looping
        '''
        o = s
        i=0
        while i < (len(s)-2):
            if s[i] == s[i+1] and s[i+1] == s[i+2]:
                s = s[:i]+s[i+1:]
                continue
            i+=1
        if o != s:
            log.debug('Removing mutiplicated chars : %s --> %s'%(o, s))
        return s

    def typo_correction(self, word):
        for char_list in self._typos:
            #We check if the word contains one of this char
            is_in = False
            for c in char_list:
                if c in word:
                    is_in = True
                    if word.count(c) > 6:
                        # Having too many duplicates crashes the code because of too many permutations
                        word = self._delete_triplicates(word)
            if is_in:
                for letters in list(itertools.permutations(char_list)):
                    # For every permutation
                    letter = letters[0]
                    replacement = letters[1]
                    for bool_list in list(itertools.product([False, True], repeat=word.count(letter))):
                        # For each occurence of the letter, we replace it or not (every combinatins are tried until something is found)
                        w = word
                        for i in range(len(bool_list)):
                            if bool_list[i]:
                                index = word.index(letter, i)
                                w = w[:index]+replacement+w[index+len(letter):]
                        if self._speller.spell(w):
                            return w
        return None

    def remove_candidates_names(self, text):
        '''
        # TODO
        This function should output the candidates found (to know to which one the tweet refers to)
        But this has to be done also in the user_mentions and hashtags..

        Removes the names of the candidates in the tweet

        :param text: the text of the tweet
        :type text: str
        :return: Corrected text
        :rtype: str
        '''
        for cand in CANDIDATES_1ST_ROUND:
            text = cand.regex().sub('', text)
        return text

    def is_correctly_spelled(self, word):
        '''
        Check if a word is correctly spelled according to the french dictionnary

        :param word: the word to check
        :type word: str
        :return: True if it is correctly spelled
        :rtype: bool
        '''
        return self._speller.spell(word)

    def remove_emojis(self, text):
        '''
        Remove emojis from a text
        :param text: Text
        :type text: str
        :return: text without emojis
        :rtype: str
        '''
        if self._emoji_pattern.findall(text):
            log.debug('Removing "%s"'%self._emoji_pattern.findall(text))
        return (self._emoji_pattern.sub('', text))

    def score(self, text):
        '''
        Scores lemmatized text
        It looks first for expressions, and then for words

        :param text: text already lemmatized
        :type words: str
        :return: total score of text
        :rtype: int
        '''

        score_pos=0
        score_neg=0

        ## We first look for expressions
        full_case_expr = self._expr_pattern.findall(text)
        exprs_found = self._expressions_dict[self._expressions_dict['phrase'].isin([e.lower() for e in full_case_expr])]

        if not exprs_found.empty:
            pola = exprs_found.groupby('polarity').count()['phrase']
            if 'negative' in pola:
                score_neg -= pola['negative']
            if 'positive' in pola:
                score_pos += pola['positive']
            for expr in full_case_expr:
                text = text.replace(expr, '')
        log.debug('Expression score : pos =  %s, neg = %s'%(score_pos, score_neg))

        ## Then we look for words
        text = text.lower().split(' ')

        words_found = self._words_dict[self._words_dict['word'].isin(text)]
        if not words_found.empty:
            pola = words_found.groupby('polarity').count()['word']
            if 'negative' in pola:
                score_neg -= pola['negative']
            if 'positive' in pola:
                score_pos += pola['positive']
        log.debug('Total score : pos = %s, neg = %s'%(score_pos, score_neg))
        return {'pos' : score_pos, 'neg': score_neg}
