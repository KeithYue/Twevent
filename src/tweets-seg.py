# coding: utf-8
from __future__ import division
import nltk
import math
from MicrosoftNgram.MicrosoftNgram import LookupService
from pprint import pprint

lookup = LookupService(model='bing-body/apr10/5')

def tokenize(sent):
    '''
    given a sent, return the tokenized wordlist
    '''
    tokens = nltk.word_tokenize(sent)
    tokens = [token for token in tokens if token not in [
        ',', '.', ':', '!', '?']]
    return tokens

def get_scp_score(segment):
    '''
    segments: a list of tokens
    return the scp score given one segment
    '''
    if(len(segment) == 0):
        return
    if(len(segment) == 1):
        return 2 * get_propability(' '.join(segment))
    pr_s = math.exp(get_propability(' '.join(segment)))
    n = len(segment)
    sum = 0
    for i in range(1, n):
        s1 = segment[0:i]
        s2 = segment[i:n]
        # print s1, s2
        pr1 = math.exp(get_propability(' '.join(s1)))
        pr2 = math.exp(get_propability(' '.join(s2)))
        pr = pr1 * pr2
        sum = sum + pr

    avg = sum / (n-1)
    # print sum, n, pr_s, avg
    scp = math.log((pr_s ** 2)/avg)

    return scp

def get_stickiness(segment):
    '''
    given one segment
    return the stickness score
    '''
    scp_score = get_scp_score(segment)

    return 2/(1 + math.exp(-scp_score))

def get_propability(phrase):
    '''
    given a string segment,
    return the prior probability of the segments
    '''
    return lookup.GetJointProbability(phrase)


class TweetSeg():

    def __init__(self, tweet):
        self.tweet = tweet
        self.tokens = tokenize(tweet)
        pass

    def tweet_segmentation(self, e = 5, u = 5):
        # using dynamic projramming
        n = len(self.tokens)
        tokens = self.tokens
        S = [[] for i in range(0,n)]
        for i in range(0, n):
            if i < u:
                S[i].append(([tokens[0:i+1]], get_stickiness(tokens[0:i+1])))

            j = i
            while j >= 1 and i - j < u:
                t2 = tokens[j:i+1]
                for segment in S[j-1]:
                    # print i, j, segment[0], t2
                    new_seg = []
                    for s in segment[0]:
                        new_seg.append(s)

                    new_seg.append(t2)
                    S[i].append((new_seg, get_stickiness(t2) + segment[1]))

                S[i] = sorted(S[i], key = lambda item: item[1], reverse=True)[0:e]
                j = j - 1
            print S[i][0]


        return S[n-1][0]






if __name__ == '__main__':
    tweet =  'After only 2 hours of sleep last night, I should probably go to sleep, right? Right. Stupid jet lag.'
    t = TweetSeg(tweet)
    print tweet
    print t.tweet_segmentation()
