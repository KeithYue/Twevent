# coding=utf-8
from twitter_nlp.python.ner.extractEntities2_for_twevent import get_ner
from twitter_nlp.python.ner.bio_parser import bio_parse
from db_connecter import twitter, tweets
from nltk.chunk.util import conllstr2tree
import Queue
import threading
import dateutil.parser
'''
this tool is to add three fields of tweets:
    ner tag
    pos + chunk tag
    event tag
'''

class TweetsChunkerThread(threading.Thread):
    def __init__(self, queue):
        '''
        The multi-thread version of tweet chunker
        '''
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            try:
                tweet, index = self.queue.get()
                tweet_text = tweet['text']

                lock.acquire()
                ner_output, chunk_output, event_output = get_ner(tweet_text, index)
                print 'The day', get_day(tweet['created_at'])
                lock.release()
                # print ner_output, chunk_output, event_output
                print bio_parse(ner_output)
                # get_chunks(chunk_output)
                # print bio_parse(event_output)

                # save the result to the database
                tweets.update(
                        {
                            '_id': tweet['_id']
                            },
                        {
                            '$set': {
                                'twitter_nlp':{
                                    'ner':bio_parse(ner_output),
                                    'chunks':get_chunks(chunk_output),
                                    'events':bio_parse(event_output)
                                    }
                                }
                            }
                        )
                print 'tweets ', tweet['_id'], 'updated!!'
                # signal the queue this task is completed
                self.queue.task_done()

            except Exception as e:
                print "An error has occured:", e
                self.queue.task_done()

def get_day(date_string):
    '''
    given a utc time string, return the day of the date
    '''
    try:
        d = dateutil.parser.parse(date_string)
        day = d.day
        return day
    except Exception as e:
        print 'an error has occured in get_day'
        return 0

def get_chunks(chuck_str):
    '''
    give a chunk str represented in conll format
    return the list of chunks
    '''
    chunks = []
    try:
        chunk_tree = conllstr2tree(chuck_str)
        # get all the chunks under the root
        for s in chunk_tree.subtrees(lambda s: s.height() > 1 and s.node != 'S'):
            # the chunk must not be the leaves and not the root of the tree
            # print s.leaves()# flaten this sub tree
            chunks.append([leaf[0] for leaf in s.leaves()])

        return chunks

    except Exception as e:
        print 'an error has occured in get_chunks', e
        return []

def main():
    # spawn a pool of threads, and pass them queue instance
    for i in range(100):
        t = TweetsChunkerThread(queue)
        t.setDaemon(True)
        t.start()

    # populate the data into the queue
    # get all the tweets in Nov.1
    for index, tweet in enumerate(tweets.find()):
        # filter out the tweets that not in the same day
        if get_day(tweet['created_at']) == day:
            queue.put((tweet, index))

    # block current thread until there is no subthread
    queue.join()

# define the consumer queue
queue = Queue.Queue()

# the model lock
lock = threading.Lock()

# which day is operating on
day = 1

if __name__ == '__main__':
    main()
