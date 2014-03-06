from db_connecter import twitter, tweets
from twitter_chucnker import get_day

# read the tweets
def main():
    for t in tweets.find()[0:10000]:
        if get_day(t['created_at']) == 1:
            if t['twitter_nlp']['chunks'] and t['twitter_nlp']['ner']:
                try:
                    print t['text'].encode('utf-8')
                    print t['twitter_nlp']['chunks']
                    print t['twitter_nlp']['ner']
                except:
                    continue

if __name__ == '__main__':
    main()
