import requests
import json
import datetime
import pytz
import re
import what3words
import os
from datetime import datetime, timezone, timedelta

def generate_session(username: str, password: str) -> requests.Session:
    # Logs in the requests session to Terrain and attaches the authentication header

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
    resp = connection.post(url, json=body, headers=headers)

    # Ensure credentials are correct
    if resp.status_code == 400:
        raise RuntimeError(resp.json())

    # Attach the auth header & return session
    connection.headers.update({
        "Authorization": resp.json()["AuthenticationResult"]["IdToken"]
    })

    return connection

def get_member_id(connection: requests.Session) -> str:
    url = "https://members.terrain.scouts.com.au/profiles"
    data = connection.get(url).json()
    return data["profiles"][0]["member"]["id"]

def get_events(connection: requests.Session, member: str) -> list:
    start_datetime = datetime.now().date().isoformat()
    end_datetime = datetime.now().date() + timedelta(days=1)
    end_datetime = end_datetime.isoformat()
    url = f"https://events.terrain.scouts.com.au/members/{member}/events?start_datetime={start_datetime}&end_datetime={end_datetime}"
    data = connection.get(url).json()
    print (json.dumps(data))
    return data

def get_event_info(connection: requests.Session, id: str):
    url = f"https://events.terrain.scouts.com.au/events/{id}"
    data = connection.get(url).json()
    return data

def message_none(wh_url, terrain_mention):
    headers = {'Content-Type': 'application/json'}
    if terrain_mention:
        content = {
            "body": "No meeting tonight, according to [Scouts | Terrain](terrain.scouts.com.au/programming)",
        }
    else:
        content = {
            "body": "No Venturer meeting tonight, according to our online calendar.\n\n*Note: If it's term-time, this may be wrong. Please refer to any amendments below.*",
        }
    data = json.dumps(content)
    response = requests.post(wh_url, headers=headers, data=data)

    if response.status_code == 200:
        print("Message sent successfully to Jandi.")
    else:
        print("Failed to send message to Jandi. Error:", response.text)

def message_meeting(content, wh_url):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(content)
    response = requests.post(wh_url, headers=headers, data=data)

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
    formatted_challenge = challenge.get(challenge_area, challenge_area)

    return formatted_challenge

def fancify_leads(leader_names):
    if len(leader_names) > 0:
        lead_string = "**Lead{}:** {}".format("s" if len(leader_names) > 1 else "", ", ".join(leader_names))
    else:
        lead_string = "No designated leader"
    return lead_string

def fancify_assists(assistant_names):
    if len(assistant_names) > 0:
        assistant_string = "**Assistant{}:** {}".format("s" if len(assistant_names) > 1 else "", ", ".join(assistant_names))
    else:
        assistant_string = "No designated assistant"
    return assistant_string

def locationw3w(loc_string):
    def find_possible_3wa(text):
        regex_search = "[^0-9`~!@#$%^&*()+\-_=[{\]}\\|'<,.>?/\";:£§º©®\s]{1,}[.｡。･・︒។։။۔።।][^0-9`~!@#$%^&*()+\-_=[{\]}\\|'<,.>?/\";:£§º©®\s]{1,}[.｡。･・︒។։။۔።।][^0-9`~!@#$%^&*()+\-_=[{\]}\\|'<,.>?/\";:£§º©®\s]{1,}"
        return re.findall(regex_search, text, flags=re.UNICODE)

    api = what3words.Geocoder(what3words_api_key)

    possible = find_possible_3wa(loc_string)

    if possible:
        try:
            json = api.autosuggest(possible[0])
        except:
            loc_string = loc_string.replace(possible[0], "(what3words error)")
            return loc_string
        markdown_link = f"[///{json['suggestions'][0]['words']}](https://w3w.co/{json['suggestions'][0]['words']})"
        if json['suggestions'][0]['country'] == 'AU':
            w3w_nearest = f"{markdown_link} (near {json['suggestions'][0]['nearestPlace']})"
        else:
            w3w_nearest = f"{markdown_link} (near {json['suggestions'][0]['nearestPlace']} - this may be incorrect!)"
        loc_string = loc_string.replace("///", "")
        loc_string = loc_string.replace(possible[0], w3w_nearest)

    return loc_string

script_dir = os.path.dirname(os.path.abspath(__file__))
filename = 'config.json'
filepath = os.path.join(script_dir, filename)

with open(filepath) as config:
    config = json.load(config)

terrain_username = config['terrain_username']
terrain_password = config['terrain_password']
youth_wh_url = config['youth_wh_url']
parent_wh_url = config['parent_wh_url']
local_timezone = config['timezone']
section = config['section']
meeting_weekday = config['meeting_weekday']
what3words_api_key = config['what3words_api_key']
name_replacements = config['name_replacements']

session = generate_session(terrain_username, terrain_password)

event_list = get_events(session, get_member_id(session))
if 'results' in event_list:
    for event in event_list['results']:
        if event['section'] == f'{section}' and event['invitee_type'] == 'unit':
            event_id = event['id']
            break
        else:
            if datetime.now().weekday() == meeting_weekday:
                message_none(youth_wh_url, True)
                message_none(parent_wh_url, False)
                quit()
            elif meeting_weekday is not None and 0 <= meeting_weekday <= 6:
                print("No events today.")
                quit()
            else:
                print("No events today, and no regular weekday set.")
                quit()
else:
    print("Error getting event list")
    quit()

event_info = get_event_info(session, event_id)

local_timezone = pytz.timezone(local_timezone)
start_datetime_local = datetime.fromisoformat(event_info['start_datetime']).astimezone(local_timezone)
end_datetime_local = datetime.fromisoformat(event_info['end_datetime']).astimezone(local_timezone)

if start_datetime_local.date() != datetime.now(local_timezone).date():
    print("Event returned does not begin today in local timezone")
    quit()

title = event_info['title']

location = locationw3w(event_info['location'])

formatted_challenge = format_challenge(event_info['challenge_area'])

if start_datetime_local.date() != end_datetime_local.date():
    formatted_start_time = start_datetime_local.strftime("%-I:%M %p, %A %-d %B")
    formatted_end_time = end_datetime_local.strftime("%-I:%M %p, %A %-d %B")
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
    "connectColor": "#99002b",
    "connectInfo": [{
        "title": title,
        "description": f"📍 {location}\n🕒 {formatted_start_time} - {formatted_end_time}\n{formatted_challenge}\n\n{description}\n\n{lead_string}\n\n{assistant_string}\n\nView on [Scouts | Terrain](terrain.scouts.com.au/programming)"
    }]
}

parent_message_content = {
    "body": "Upcoming event for Venturer Scouts",
    "connectColor": "#99002b",
    "connectInfo": [{
        "title": title,
        "description": f"📍 {location}\n🕒 {formatted_start_time} - {formatted_end_time}"
    }]
}

message_meeting(youth_message_content, youth_wh_url)
message_meeting(parent_message_content, parent_wh_url)

print(youth_message_content)
print(parent_message_content)