import requests
import json
import datetime
import pytz
import re
import what3words
from datetime import date, datetime, timedelta

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

def get_member(connection: requests.Session) -> str:
    # Get the Terrain UUID for your member account
    url = "https://members.terrain.scouts.com.au/profiles"
    data = connection.get(url).json()
    return data["profiles"][0]["member"]["id"]

def format_datetime(dt):
    # Format datetime as 12-hour time without seconds
    return dt.strftime("%-I:%M %p")

def get_events(connection: requests.Session, member: str) -> list:
    # Check for upcoming events (default lookahead is 1 day)
    current_date = datetime.now().date()
    tomorrow_date = current_date + timedelta(days=1)
    start_datetime = current_date.isoformat()
    end_datetime = tomorrow_date.isoformat()
    url = f"https://events.terrain.scouts.com.au/members/{member}/events?start_datetime={start_datetime}&end_datetime={end_datetime}"
    data = connection.get(url).json()
    print (json.dumps(data))
    return data

def get_event_info(connection: requests.Session, id: str):
    # Get info on an event given its UUID
    url = f"https://events.terrain.scouts.com.au/events/{id}"
    data = connection.get(url).json()
    return data

def message_none(wh_url):
    # Post Jandi message confirming no meeting
    webhook_url = wh_url
    headers = {'Content-Type': 'application/json'}
    content = {
        "body": "No meeting tonight, according to [Scouts | Terrain](terrain.scouts.com.au/programming)",
    }
    data = json.dumps(content)
    response = requests.post(webhook_url, headers=headers, data=data)

    if response.status_code == 200:
        print("Message sent successfully to Jandi.")
    else:
        print("Failed to send message to Jandi. Error:", response.text)

def message_meeting(content, wh_url):
    # Post Jandi message with event details
    webhook_url = wh_url
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(content)
    response = requests.post(webhook_url, headers=headers, data=data)

    if response.status_code == 200:
        print("Message sent successfully to Jandi.", json.dumps(content))
    else:
        print("Failed to send message to Jandi. Error:", response.text)    

def locationw3w(loc_string):
    # Find w3w location strings
    def findPossible3wa(text):
        regex_search = "[^0-9`~!@#$%^&*()+\-_=[{\]}\\|'<,.>?/\";:£§º©®\s]{1,}[.｡。･・︒។։။۔።।][^0-9`~!@#$%^&*()+\-_=[{\]}\\|'<,.>?/\";:£§º©®\s]{1,}[.｡。･・︒។։။۔።।][^0-9`~!@#$%^&*()+\-_=[{\]}\\|'<,.>?/\";:£§º©®\s]{1,}"
        return re.findall(regex_search, text, flags=re.UNICODE)

    # Define API key
    api = what3words.Geocoder("API KEY")

    possible = findPossible3wa(loc_string)

    if possible:
        # Convert w3w string to link with confirmation location
        json = api.convert_to_coordinates(possible[0])
        markdown_link = f"[///{json['words']}](https://w3w.co/{json['words']})"
        w3w = f"{markdown_link} (near {json['nearestPlace']})"
        loc_string = loc_string.replace("///", "")
        loc_string = loc_string.replace(possible[0], w3w)

    return loc_string

def format_list(items):
    # List names in a human-friendly way with correct English syntax
    if len(items) == 1:
        return items[0]
    elif len(items) > 1:
        return ", ".join(items)
    else:
        return ""

# Define login and webhook details
terrain_username = "USERNAME"
terrain_password = "PASSWORD"
wh_url = "WEBHOOK URL"
session = generate_session(terrain_username, terrain_password)
member = get_member(session)
event_list = get_events(session, member)

# Set up search for events
venturer_event_found = False 

# Find Venturer Unit events
if 'results' in event_list:
    for event in event_list['results']:
        if event['section'] == 'venturer' and event['invitee_type'] == 'unit':
            meeting_id = event['id']
            venturer_event_found = True
            break  # Exit the loop after finding the first 'venturer' event

# If no event is found, check whether there should be one and message if there should
if not venturer_event_found:
    if datetime.now().weekday() == 3:
        message_none(wh_url)
        quit()
    else:
        print("No events today")
        quit()

# Get more info on a found event
data = get_event_info(session, meeting_id)

# Parse event title
title = data['title']

# Parse leader names
leader_members = data['attendance']['leader_members']
leader_names = [member['first_name'] + ' ' + member['last_name'] for member in leader_members]

# Parse assistant names
assistant_members = data['attendance']['assistant_members']
assistant_names = [member['first_name'] + ' ' + member['last_name'] for member in assistant_members]

# Parse location and challenge area
location = data['location']
challenge_area = data['challenge_area']

# Define timezone
timezone = pytz.timezone('Australia/Sydney')

# Parse start and end datetimes as UTC and convert to specified timezone
for event in data:
    start_datetime_str = data['start_datetime']
    end_datetime_str = data['end_datetime']

    # Parse the datetimes as UTC
    start_datetime_utc = datetime.fromisoformat(start_datetime_str)
    end_datetime_utc = datetime.fromisoformat(end_datetime_str)

    # Convert to timezone
    start_datetime_sydney = start_datetime_utc.astimezone(timezone)
    end_datetime_sydney = end_datetime_utc.astimezone(timezone)

    # Format datetime as 12-hour time without seconds
    formatted_start_time = format_datetime(start_datetime_sydney)
    formatted_end_time = format_datetime(end_datetime_sydney)

# Parse description
if 'description' in data:
    description = data['description']
else: description = "No description given"

# Convert challenge area to human-readable string
challenge = {
    "community": "🌏 Community Challenge",
    "outdoors": "🏕️ Outdoor Challenge",
    "creative": "💡 Creative Challenge",
    "personal_growth": "🌱 Personal Growth Challenge",
}
challenge_cleaned = challenge.get(challenge_area, challenge_area)

# Apply above function to leader and assistant names
lead_string = format_list(leader_names)
assistant_string = format_list(assistant_names)

# Output leader names (or lack thereof)
if len(leader_names) > 0:
    lead_cleaned = "**Lead{}:** {}".format("s" if len(leader_names) > 1 else "", ", ".join(leader_names))
else:
    lead_cleaned = "No designated leader"

# Output assistant names (or lack thereof)
if len(assistant_names) > 0:
    assistant_cleaned = "**Assistant{}:** {}".format("s" if len(assistant_names) > 1 else "", ", ".join(assistant_names))
else:
    assistant_cleaned = "No designated assistant"

# Convert w3w locations to clickable links
location = locationw3w(location)

# Define webhook post content using parsed information from Terrain
content = {
    "body": "Upcoming event from Scouts | Terrain",
    "connectColor": "#00C473",
    "connectInfo": [{
        "title": title,
        "description": f"📍 {location}\n🕒 {formatted_start_time} - {formatted_end_time}\n{challenge_cleaned}\n\n{description}\n\n{lead_cleaned}\n\n{assistant_cleaned}\n\nView on [Scouts | Terrain](terrain.scouts.com.au/programming)"
    }]
}

# Post event information on Jandi (main function)
message_meeting(content, wh_url)

# Print webhook post for debugging
print(content)