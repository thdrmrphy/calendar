# Calendar

## Scouts | Terrain -> JANDI incoming webhook integration

Calendar is a small Python script you can run as a daily cronjob. Given a login to Scouts | Terrain, it will find any events for the current day in a specified section that the account has access to, and post details on two JANDI topics.

See all features below.

The base of this code is from [aiden2480/crest](https://github.com/aiden2480/crest) back when it was written in Python. This wouldn't exist if it weren't for that project!

## Dependencies

```
json
re
os
datetime
functools
requests
pytz
what3words
```

## config.json


| Key                  | Default value                | Description                                                                                                                                                               |
| -------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `terrain_username`   | `abc-123456`                 | Your state, then a hyphen, then your member number. For example, `nsw-1234567`.                                                                                           |
| `terrain_password`   | `password`                   | Your password for Terrain.                                                                                                                                                |
| `youth_wh_url`       | `https://wh.jandi.com/...`   | The URL for the webhook set up in JANDI for the youth members' topic.                                                                                                     |
| `parent_wh_url`      | `https://wh.jandi.com/...`   | The URL for the webhook set up in JANDI for the parents' topic.                                                                                                           |
| `timezone`           | `Australia/Sydney`           | Your timezone (automatically corrects for daylight saving)                                                                                                                              |
| `section`            | `venturer`                   | The Section you wish to notify. This will be `joey`, `cub`, `scout`, `venturer` or `rover`.                                                                               |
| `meeting_weekday`    | `null`                       | The day of the week on which the bot will send a "No meeting tonight" message if there's no event. Monday is `0`, Sunday is `6`. `null` disables this feature.            |
| `what3words_api_key` | `ABCDEFGH`                   | The API key from what3words. Requests are free and unlimited for this script.                                                                                             |
| `name_replacements`  | `"John Smith": "Fred Smith"` | Replace a full name with another full name. Useful where a person's name in Terrain is not what they are usually called. This affects mentions of Leaders and Assistants. |

## Features

- Sends a message (see sample output below) to the youth members' JANDI topic with full event details. This includes:
    - Name
    - Location (including what3words addresses)
    - Date and time (dynamically, based on event time and length)
    - Challenge Area
    - Description
    - Leaders and Assistants
    - A link to Terrain
- Sends a message to any parents' topic with concise details. This includes:
    - Name
    - Location (including what3words addresses)
    - Date and time (dynamically, based on event time and length)
- Makes any what3words addresses clickable and highlights where they are in normal terms. Also highlights when they may be incorrect (i.e. outside Australia)
- Only notifies of events starting in the next 24 hours after the script is run. Due to the way Terrain stores and retrieves events in UTC by default, this override comes in handy. It also means that events starting early (such as a dawn service for ANZAC Day) are communicated the day before, instead of after they commence. 
- Given a regular meeting weekday set in the configuration, the script can inform JANDI users if there's nothing on. For example, if your meetings are normally on Tuesdays, but one week it's cancelled, the script lets everyone know.
- The colour on the left of the JANDI message is in-line with Section branding.
- Replaces names as specified in the configuration. 

and more...

## Example output

Youth see:

![DragonSkin 2024](https://github.com/thdrmrphy/calendar/assets/130824397/beee215f-acb9-4ae0-af38-49442b1b0f7e)

Parents see:

![Parent version](https://github.com/thdrmrphy/calendar/assets/130824397/9a537341-f5d3-4719-8647-159494658120)

Another example:

![Excuse the bread](https://github.com/thdrmrphy/calendar/assets/130824397/17697d85-9464-4a7a-a193-977b5f53ef9e)

## To-do

- Allow for what3words API bypass
- Allow for parent topic bypass
- Remove Scouts | Terrain link (cleanup)
- Remove Leads/Assists when not designated (cleanup)