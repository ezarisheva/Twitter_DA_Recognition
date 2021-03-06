__author__ = 'snownettle'
import json


def import_conversations(collection, conversations):
    conversation_number = len(conversations)
    count = 1
    for conversation in conversations:
        data = dict()
        data['conversation_number'] = count
        count += 1
        root_tweet_id = conversation.root_tweet
        root_tweet_id = int(root_tweet_id)
        data['root_tweet_id'] = root_tweet_id
        # information about depth and width
        data['depth'] = conversation.find_depth()
        data['width'] = conversation.find_width()
        conversation_tree = conversation.get_conversation_tree()
        find_children(conversation_tree, root_tweet_id, data)
        json.dumps(data)
        collection.insert(data)
        if count % 1000 == 0:
            print ('in progress...' + '%.2f' % (count*100/float(conversation_number)) + '%')


def find_children(conversation, parent_tweet_id, data):
    list_of_children = conversation.is_branch(parent_tweet_id)
    parent_tweet_id = str(parent_tweet_id)
    if len(list_of_children) == 0:
        data[parent_tweet_id] = None
    else:
        data[parent_tweet_id] = list_of_children
        for child in list_of_children:
            find_children(conversation, child, data)

