# dialogue_reconstruction.py

import pandas as pd
from datetime import datetime
from config import load_config

def reconstruct_twcs_dialogues(df):
    """
    Reconstructs conversation dialogues from a Pandas DataFrame of TWCS tweets.
    Identifies user and agent turns based on predefined agent IDs.
    This function expects a Pandas DataFrame (after Dask .compute()).
    """
    config = load_config()
    agent_ids = config['agent_ids']['twcs'] # Use TWCS specific agent IDs

    # Ensure 'created_at' is datetime and sort by it for robust mapping
    # This sort is crucial for correct chronological ordering in dialogues
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values(by='created_at').reset_index(drop=True)

    tweet_map = df.set_index('tweet_id').to_dict(orient='index')
    
    conversations = []
    processed_tweet_ids = set()

    for tweet_id, tweet_info in tweet_map.items():
        if tweet_id in processed_tweet_ids:
            continue

        current_thread_tweets = []
        
        # --- Step 1: Trace back to find the earliest root of the conversation ---
        # This handles cases where we start from a reply and need to find the beginning
        temp_tweet_id = tweet_id
        temp_tweet = tweet_map.get(temp_tweet_id)
        while temp_tweet:
            current_thread_tweets.insert(0, temp_tweet) # Add to the beginning of the list
            processed_tweet_ids.add(temp_tweet_id)

            found_parent = False
            for parent_id in temp_tweet['in_response_to_tweet_id']:
                if parent_id in tweet_map and parent_id not in processed_tweet_ids:
                    temp_tweet_id = parent_id
                    temp_tweet = tweet_map[parent_id]
                    found_parent = True
                    break # Only trace one parent for simplicity in tree-like structures
            if not found_parent:
                temp_tweet = None # No more unprocessed parents in this branch

        # --- Step 2: Trace forward from the current set of thread tweets ---
        # Use a queue to find all replies starting from the identified thread.
        # This ensures we capture all branches of a conversation.
        queue = list(current_thread_tweets)
        idx = 0
        MAX_QUEUE_PROCESS = 500 # Safety limit to prevent infinite loops for malformed data
        while idx < len(queue) and idx < MAX_QUEUE_PROCESS:
            current_t = queue[idx]
            for response_id in current_t['response_tweet_id']:
                if response_id in tweet_map and response_id not in processed_tweet_ids:
                    response_tweet = tweet_map[response_id]
                    current_thread_tweets.append(response_tweet)
                    processed_tweet_ids.add(response_tweet['tweet_id'])
                    queue.append(response_tweet) # Add to queue to process its replies
            idx += 1

        # Sort the entire thread by time to ensure chronological order for the dialogue
        current_thread_tweets.sort(key=lambda t: t['created_at'])

        if current_thread_tweets:
            dialogue_sequence = []
            for t in current_thread_tweets:
                author_type = 'agent' if t['author_id'] in agent_ids else 'user'
                dialogue_sequence.append({
                    'tweet_id': t['tweet_id'],
                    'author_id': t['author_id'],
                    'type': author_type,
                    'text': t['cleaned_text'],
                    'created_at': t['created_at']
                })
            conversations.append(dialogue_sequence)

    return conversations

def reconstruct_conversation3k_dialogues(df):
    """
    Placeholder for reconstructing dialogues for Conversation3k.
    The implementation will depend on the exact structure of the Conversation3k dataset.
    It might involve grouping by a 'conversation_id' and sorting turns.
    """
    config = load_config()
    agent_ids = config['agent_ids']['conversation3k']

    # Example: If Conversation3k is already semi-structured by conversation_id
    # df = df.sort_values(by=['conversation_id', 'created_at'])
    conversations = []
    # Logic to group and reconstruct based on conversation3k structure
    # For now, it will return dialogues assuming each row is a simple text or turn.
    # This will need to be refined based on the actual conversation3k structure.
    for index, row in df.iterrows():
        # This is a very basic placeholder for non-linked data
        author_type = 'agent' if row['author_id'] in agent_ids else 'user'
        conversations.append([{
            'tweet_id': row['tweet_id'], # Using tweet_id as generic message_id
            'author_id': row['author_id'],
            'type': author_type,
            'text': row['cleaned_text'],
            'created_at': row['created_at']
        }])
    print("Warning: Conversation3k dialogue reconstruction is a placeholder and needs actual implementation.")
    return conversations

# RSCIS likely doesn't need dialogue reconstruction as it's assumed to be single-turn texts.
def reconstruct_rscis_data(df):
    """
    RSCIS data is assumed to be single-turn, so no reconstruction needed.
    It's treated as a list of single-turn dialogues for consistency.
    """
    conversations = []
    for index, row in df.iterrows():
        conversations.append([{
            'tweet_id': row['tweet_id'], # Using tweet_id as generic message_id
            'author_id': row['author_id'],
            'type': 'user', # Assuming RSCIS entries are primarily user queries/statements
            'text': row['cleaned_text'],
            'created_at': row['created_at']
        }])
    return conversations

