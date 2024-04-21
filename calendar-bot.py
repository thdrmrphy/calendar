# Python script to post event information from Scouts | Terrain on JANDI topics.

import json
import re
import os
from datetime import datetime, timedelta
from functools import lru_cache

import requests
import pytz
import what3words

def generate_session(username: str, password: str) -> requests.Session:
    connection = requests.Session()

    body = {
        "ClientId": "6v98tbc09aqfvh52fml3usas3c",
        "AuthFlow": "USER_PASSWORD_AUTH",
        "AuthParameters": {
            "USERNAME": username,
            "PASSWORD": password,
        },
    }

    headers = {
        "Content-Type": "application/x-amz-json-1.1",
        "X-amz-target": "AWSCognitoIdentityProviderService.InitiateAuth",
    }

    url = "https://cognito-idp.ap-southeast-2.amazonaws.com/"
    resp = connection.post(url, json=body, headers=headers, timeout=10)

    if resp.status_code == 400:
        raise RuntimeError(resp.json())

    connection.headers.update({
        "Authorization": resp.json()["AuthenticationResult"]["IdToken"]
    })

    return connection

def get_member_id(connection: requests.Session) -> str:
    url = "https://members.terrain.scouts.com.au/profiles"
    member_data = connection.get(url).json()
    return member_data["profiles"][0]["member"]["id"]

def get_events(connection: requests.Session, member: str) -> list:
    start_datetime = (datetime.now().date() - timedelta(days=1)).isoformat()
    end_datetime = (datetime.now().date() + timedelta(days=1)).isoformat()
    url = f"https://events.terrain.scouts.com.au/members/{member}/events?start_datetime={start_datetime}&end_datetime={end_datetime}"
    event_data = connection.get(url).json()
    return event_data

@lru_cache(maxsize=None)
def get_event_info(connection: requests.Session, id: str):
    url = f"https://events.terrain.scouts.com.au/events/{id}"
    event_data = connection.get(url).json()
    return event_data

def jandi_none(wh_url, terrain_mention):
    headers = {'Content-Type': 'application/json'}
    if terrain_mention:
        content = {
            "body": "No meeting tonight, according to [Scouts | Terrain](terrain.scouts.com.au/programming)",
        }
    else:
        content = {
            "body": f"**No {section_full_name} meeting tonight, according to our online calendar.**\n\n*Note: If it's term-time, this may be wrong. Please refer to any amendments below.*",
        }
    message_data = json.dumps(content)
    response = requests.post(wh_url, headers=headers, data=message_data, timeout=10)

    if response.status_code == 200:
        print("Message sent successfully to Jandi.")
    else:
        print("Failed to send message to Jandi. Error:", response.text)

def jandi_details(content, wh_url):
    headers = {'Content-Type': 'application/json'}
    message_data = json.dumps(content)
    response = requests.post(wh_url, headers=headers, data=message_data, timeout=10)

    if response.status_code == 200:
        print("Message sent successfully to Jandi.", json.dumps(content))
    else:
        print("Failed to send message to Jandi. Error:", response.text)   

def replace_names(members):
    names = [member['first_name'] + ' ' + member['last_name'] for member in members]
    updated_names = []
    for name in names:
        updated_name = name_replacements.get(name, name)
        updated_names.append(updated_name)

    return updated_names

def format_challenge(challenge_area):
    challenge = {
        "community": "🌏 Community Challenge",
        "outdoors": "🏕️ Outdoor Challenge",
        "creative": "💡 Creative Challenge",
        "personal_growth": "🌱 Personal Growth Challenge",
    }
    challenge_replace = challenge.get(challenge_area, challenge_area)

    return challenge_replace

def fancify_leads(leader_names):
    if len(leader_names) > 0:
        lead_join = "**Lead{}:** {}".format("s" if len(leader_names) > 1 else "", ", ".join(leader_names))
    else:
        lead_join = "No designated leader"
    return lead_join

def fancify_assists(assistant_names):
    if len(assistant_names) > 0:
        assistant_join = "**Assistant{}:** {}".format("s" if len(assistant_names) > 1 else "", ", ".join(assistant_names))
    else:
        assistant_join = "No designated assistant"
    return assistant_join

def location_append_w3w(loc_string):
    def find_possible_3wa(text):
        regex_search = "[^0-9`~!@#$%^&*()+\-_=[{\]}\\|'<,.>?/\";:£§º©®\s]{1,}[.｡。･・︒។։။۔።।][^0-9`~!@#$%^&*()+\-_=[{\]}\\|'<,.>?/\";:£§º©®\s]{1,}[.｡。･・︒។։။۔።।][^0-9`~!@#$%^&*()+\-_=[{\]}\\|'<,.>?/\";:£§º©®\s]{1,}"
        return re.findall(regex_search, text, flags=re.UNICODE)

    api = what3words.Geocoder(what3words_api_key)

    possible = find_possible_3wa(loc_string)

    if possible:
        try:
            api_response = api.autosuggest(possible[0])
        except:
            loc_string = loc_string.replace(possible[0], "(what3words error)")
            return loc_string
        markdown_link = f"[///{api_response['suggestions'][0]['words']}](https://w3w.co/{json['suggestions'][0]['words']})"
        if api_response['suggestions'][0]['country'] == 'AU':
            w3w_nearest = f"{markdown_link} (near {api_response['suggestions'][0]['nearestPlace']})"
        else:
            w3w_nearest = f"{markdown_link} (near {api_response['suggestions'][0]['nearestPlace']} - this may be incorrect!)"
        loc_string = loc_string.replace("///", "")
        loc_string = loc_string.replace(possible[0], w3w_nearest)

    return loc_string

def event_date_filter(start_datetime):
    start_datetime_local = datetime.fromisoformat(start_datetime).astimezone(local_timezone)
    time_difference = start_datetime_local - datetime.now(local_timezone)

    if not timedelta(hours=0) <= time_difference <= timedelta(hours=24):
        print(f"Event does not begin in the next 24 hours;")
        return False
    
    return True

def send_message(event_id):
    event_info = get_event_info(session, event_id)
    
    title = event_info['title']

    location = location_append_w3w(event_info['location'])

    formatted_challenge = format_challenge(event_info['challenge_area'])

    start_datetime_local = datetime.fromisoformat(event_info['start_datetime']).astimezone(local_timezone)
    end_datetime_local = datetime.fromisoformat(event_info['end_datetime']).astimezone(local_timezone)

    if start_datetime_local.date() != end_datetime_local.date():
        formatted_start_time = start_datetime_local.strftime("%-I:%M %p, %A %-d %B")
        formatted_end_time = end_datetime_local.strftime("%-I:%M %p, %A %-d %B")
    elif start_datetime_local.date() != datetime.now(local_timezone).date():
        formatted_start_time = start_datetime_local.strftime("Tomorrow (%A %-d %B) %-I:%M %p")
        formatted_end_time = end_datetime_local.strftime("%-I:%M %p")
    else:
        formatted_start_time = start_datetime_local.strftime("%-I:%M %p")
        formatted_end_time = end_datetime_local.strftime("%-I:%M %p")

    if 'description' in event_info:
        description = event_info['description']
    else: description = "No description given"

    lead_string = fancify_leads(replace_names(event_info['attendance']['leader_members']))
    assistant_string = fancify_assists(replace_names(event_info['attendance']['assistant_members']))

    youth_message_content = {
        "body": "Upcoming event from Scouts | Terrain",
        "connectColor": f"{section_colour}",
        "connectInfo": [{
            "title": title,
            "description": f"📍 {location}\n🕒 {formatted_start_time} - {formatted_end_time}\n{formatted_challenge}\n\n{description}\n\n{lead_string}\n{assistant_string}\n\nView on [Scouts | Terrain](terrain.scouts.com.au/programming)"
        }]
    }

    parent_message_content = {
        "body": f"Upcoming event for {section_full_name}s",
        "connectColor": f"{section_colour}",
        "connectInfo": [{
            "title": title,
            "description": f"📍 {location}\n🕒 {formatted_start_time} - {formatted_end_time}"
        }]
    }

    jandi_details(youth_message_content, youth_wh_url)
    jandi_details(parent_message_content, parent_wh_url)

    print(youth_message_content)
    print(parent_message_content)

def process_event(event_id):
    event_info = get_event_info(session, event_id)
    print(f"Event: {event_info['title']}\nJSON:\n" + json.dumps(event_info))
    send_message(event_id)

filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
with open(filepath) as config:
    config = json.load(config)

try:
    terrain_username = config['terrain_username']
    terrain_password = config['terrain_password']
    youth_wh_url = config['youth_wh_url']
    parent_wh_url = config['parent_wh_url']
    local_timezone = config['timezone']
    section = config['section']
    meeting_weekday = config['meeting_weekday']
    what3words_api_key = config['what3words_api_key']
    name_replacements = config['name_replacements']
except KeyError as e:
    print(f"Configuration error: {e} is missing in the configuration.")

local_timezone = pytz.timezone(local_timezone)

section_names = {
    "joey": "Joey Scout",
    "cub": "Cub Scout",
    "scout": "Scout",
    "venturer": "Venturer Scout",
    "rover": "Rover Scout"
}
section_full_name = section_names.get(section, section)

section_colours = {
    "joey": "#b86125",
    "cub": "#ffc72c",
    "scout": "#00b140",
    "venturer": "#9d2235",
    "rover": "#da291c"
}
section_colour = section_colours.get(section, section)

session = generate_session(terrain_username, terrain_password)
event_list = get_events(session, get_member_id(session))

if not 'results' in event_list:
    print("Error getting event list")
    quit()
elif not event_list['results']:
    print("No events returned.")
    event_today = False
else:
    print(json.dumps(event_list))
    event_today = False

for event in event_list['results']:
    if event['section'] == f'{section}' and event['invitee_type'] == 'unit' and event_date_filter(event['start_datetime']):
        event_today = True
        event_id = event['id']
        print(event_id)
        process_event(event_id)
    else:
        print(f"Event {event['id']} does not fit criteria (datetime/unit)")

if event_today == False:
    if datetime.now().weekday() == meeting_weekday:
        print("No event on regular meeting day. Sending message.")
        jandi_none(youth_wh_url, True)
        jandi_none(parent_wh_url, False)
        quit()
    elif meeting_weekday is not None and 0 <= meeting_weekday <= 6:
        print("No events today.")
        quit()
    else:
        print("No events today, and no regular weekday set.")
        quit()
