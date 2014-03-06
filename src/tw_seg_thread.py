# coding=utf-8

# This script is to tag all the tweets in the mongodb database
import Queue
import threading
from tweets_seg import TweetSeg
from db_connecter import twitter, tweets

class TweetsSegThread(threading.Thread):
    def __init__(self, queue):
        '''
        the multi-thread version of tweets segmentation
        '''
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            try:
                # get a tweet to be segged
                tweet_id, tweet, index = self.queue.get()

                # print self.getName()
                # new segmentation
                print tweet
                seg = TweetSeg(tweet)
                segments = seg.tweet_segmentation()
                print segments

                # update the database with the segmentation information
                print 'updating the tweets: ', tweet_id, 'NO %d' % index
                lock.acquire()
                tweets.update(
                        {
                            '_id': tweet_id
                            },
                        {
                            '$set':{
                                'segments': segments
                                }
                            }
                        )
                lock.release()
                print 'update complete!'

                # signal the queue the task is done
                self.queue.task_done()
            except Exception as e:
                print e
                self.queue.task_done()

def main():
    #spawn a pool of threads, and pass them queue instance
    for i in range(1):
        t = TweetsSegThread(queue)
        t.setDaemon(True)
        t.start()

    #populate queue with data
    for index, tweet in enumerate(tweets.find()):
        # filter out those who has segments
        if not tweet.has_key('segments'):
            # print 'putting number %d into queue.' % index
            queue.put((tweet['_id'], tweet['text'], index))

    queue.join()


queue = Queue.Queue()

# database lock
lock = threading.Lock()

if __name__ == '__main__':
    main()
