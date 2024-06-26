import requests
import csv
import time
import sys
from datetime import datetime

access_token = ''
group_id = ''
base_url = 'https://api.groupme.com/v3'

def fetch_messages(group_id, access_token):
    messages = []
    url = f"{base_url}/groups/{group_id}/messages"
    params = {'token': access_token, 'limit': 100}
    last_id = None
    total_fetched = 0  
    while True:
        if last_id:
            params['before_id'] = last_id

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Check for HTTP errors
            batch = response.json()['response']['messages']
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 429:
                print("Rate limit exceeded. Waiting 60 seconds before retrying...")
                time.sleep(60)
                continue  
            else:
                print(f"HTTP error occurred: {http_err}")
                break
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

        if not batch:
            break  

        messages.extend(batch)
        last_id = batch[-1]['id']  
        total_fetched += len(batch)  
        print(f"Total messages fetched: {total_fetched}")  
    return messages

def save_messages_to_csv(messages, filename):
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'Date', 'Time', 'Message', 'Like Count', 'User ID', 'Liked By', 'Attachments', 'Profile Picture', 'Mention' ,'System'])

            for msg in messages:
                name = msg.get('name', '')
                created_at_date = datetime.fromtimestamp(msg['created_at']).strftime('%m/%d/%Y')
                created_at_time = datetime.fromtimestamp(msg['created_at']).strftime('%H:%M:%S')
                text = msg.get('text', '')
                like_count = len(msg.get('favorited_by', []))
                user_id = msg.get('user_id', 'Unknown')
                liked_by = ','.join(msg.get('favorited_by', []))
                attachments = ' , '.join([att['url'] for att in msg.get('attachments', []) if 'url' in att])
                profile_picture = msg.get('avatar_url', 'No picture')
                try: 
                    mentioned = ','.join(
                        [str(uid) for attachment in msg.get('attachments', [])
                         if attachment['type'] == 'mentions'
                         for uid in attachment.get('user_ids', [])]
                    )
                except Exception as e2:
                    mentioned = 'Unknown'

                system = msg.get('system', False)
                writer.writerow([name, created_at_date, created_at_time, text, like_count, user_id, liked_by, attachments, profile_picture, mentioned, system])
    except Exception as e:
        print(f"Failed to save messages: {e}")

try:
    messages = fetch_messages(group_id, access_token)
    save_messages_to_csv(messages, 'groupme_chat_history.csv')
    print("Messages have been successfully saved to 'groupme_chat_history.csv'.")
except Exception as e:
    print(f"An error occurred while fetching or saving messages: {e}")
    sys.exit(1)
