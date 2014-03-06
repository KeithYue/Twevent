# coding: utf-8
from __future__ import division
import nltk
import math
import abc
from MicrosoftNgram.MicrosoftNgram import LookupService
from happyfuntokenizing import Tokenizer
from pprint import pprint

class TweetSeg:

    def __init__(self, tweet):
        self.tweet = tweet
        self.lookup = LookupService(model='bing-body/apr10/5')
        self.toz = Tokenizer()
        self.tokens = self.tokenize(tweet)
        pass

    def tokenize(self, sent):
        tokens = sent.split(' ')
        tokens = [ w for w in tokens if w not in [
            '.', ',', '?', ':'
            ]]

        return tokens

    def len_normalization(self,segment):
        l = len(segment)
        if l == 1:
            return 1
        else:
            return (l-1)/l

    def get_scp_score(self, segment):
        '''
        segments: a list of tokens
        return the scp score given one segment
        '''
        if(len(segment) == 0):
            return
        if(len(segment) == 1):
            return 2 * self.get_propability(' '.join(segment))
        pr_s = math.exp(self.get_propability(' '.join(segment)))
        n = len(segment)
        sum = 0
        for i in range(1, n):
            s1 = segment[0:i]
            s2 = segment[i:n]
            # print s1, s2
            pr1 = math.exp(self.get_propability(' '.join(s1)))
            pr2 = math.exp(self.get_propability(' '.join(s2)))
            pr = pr1 * pr2
            sum = sum + pr

        avg = sum / (n-1)
        # print sum, n, pr_s, avg
        scp = math.log((pr_s ** 2)/avg)
        return scp

    def get_stickiness(self, segment):
        '''
        given one segment
        return the stickness score
        '''
        scp_score = self.get_scp_score(segment)
        length_normalization = self.len_normalization(segment)

        stickness =  2/(1 + math.exp(-scp_score))
        stickness *= length_normalization

        return stickness

    def get_propability(self, phrase):
        '''
        given a string segment,
        return the prior probability of the segments
        '''
        return self.lookup.GetJointProbability(phrase)

    def tweet_segmentation(self, e = 5, u = 5):
        # using dynamic projramming
        n = len(self.tokens)
        tokens = self.tokens
        S = [[] for i in range(0,n)]
        for i in range(0, n):
            if i < u:
                S[i].append(([tokens[0:i+1]], self.get_stickiness(tokens[0:i+1])))

            j = i
            while j >= 1 and i - j < u:
                t2 = tokens[j:i+1]
                for segment in S[j-1]:
                    # print i, j, segment[0], t2
                    new_seg = []
                    for s in segment[0]:
                        new_seg.append(s)

                    new_seg.append(t2)
                    S[i].append((new_seg, self.get_stickiness(t2) + segment[1]))

                S[i] = sorted(S[i], key = lambda item: item[1], reverse=True)[0:e]
                j = j - 1
            print S[i][0]


        return S[n-1][0]

if __name__ == '__main__':
    # test
    tweet =  '@alow_em_gee oh my god'
    t = TweetSeg(tweet)
    print tweet
    print t.tweet_segmentation()
