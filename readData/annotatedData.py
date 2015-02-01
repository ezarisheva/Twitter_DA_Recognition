__author__ = 'snownettle'
import glob
import os
import csv
import re
from json import JSONEncoder
from mongoDB import importAnnotatedData


def read_annotated_docs(directory_path, collection_raw_twitter_data, collection_annotated_data):
    conversation_id = 0
    tweet_id = 0
    token = ''
    tag = ''
    data = {}
    json_data = None
    for directory_name in glob.iglob(os.path.join(directory_path,'*.*')):
        for filename in glob.iglob(os.path.join(directory_name, '*.tsv')):
            with open(filename) as f:
                #print filename
                content = csv.reader(f, delimiter='\t')
                previous_row = ' '
                for row in content:
                    if len(row) is 0:
                        if conversation_id is not '1':
                            # in_replay_to_status_id = find_in_replay_to_the_status(collection_raw_twitter_data,
                            #                                                       data['tweet_id'])
                            # data['in_replay_to_status_id'] = in_replay_to_status_id
                            importAnnotatedData.importAnnotatedData(data, collection_annotated_data)
                        else:
                            continue
                    else:
                        if check_if_new_thread(row) == True:
                            conversation_id = '1'
                        if '#id' in row[0]:
                            conversation_id = re.split('id=', row[0])[1]
                            data = {}
                            data['conversation_id'] = conversation_id
                        if len(previous_row) is not 0 and '#id' in previous_row[0] and conversation_id is not '1':
                            tweet_id = re.split('id=', row[0])[1]
                            tweet_id = re.split(' user', tweet_id)[0]
                            data['tweet_id'] = tweet_id
                        if conversation_id == re.split('-', row[0])[0] and conversation_id is not '1':
                            #######SPLIT NUMBERS!
                            token = row[1].replace('.', '_')
                            tag = row[2]
                            data[token] = tag
                    previous_row = row
                #print content


def find_in_replay_to_the_status(collection, tweet_id):
    print tweet_id
    tweet = collection.find({'id':tweet_id})
    #print tweet.count()
    return tweet[0]['in_reply_to_status_id']


def find_annotated_tweet_id(row):
    if '#id' in row[0]:
        return re.split('id=', row[0])[1]
        # if 'user' not in t:
        #     return t
        #     #print re.split(' user', t)[0]
        # else:
        #     print t
        #print 'yes'




def check_if_new_thread(row):
    if 'webanno.custom.DialogActs' in row[0] or '#text=New Thread size=' in row[0]:
        return True
    else:
        return False
#def find_tweet_id(row):