# Calendar

## Scouts | Terrain -> JANDI incoming webhook integration

### Currently under redevelopment.

---

Calendar is a small Python script you can run as a daily cronjob. Given a login to Scouts | Terrain, it will find any events for the current day in a specified section that the account has access to, and post details on two JANDI topics.

See all features below.

## Dependencies

```
requests
json
datetime
pytz
re
what3words
os
```

## config.json


| Key                  | Default value                | Description                                                                                                                                                               |
| -------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `terrain_username`   | `abc-123456`                 | Your state, then a hyphen, then your member number. For example, `nsw-1234567`.                                                                                           |
| `terrain_password`   | `password`                   | Your password for Terrain.                                                                                                                                                |
| `youth_wh_url`       | `https://wh.jandi.com/...`   | The URL for the webhook set up in JANDI for the youth members' topic.                                                                                                     |
| `parent_wh_url`      | `https://wh.jandi.com/...`   | The URL for the webhook set up in JANDI for the parents' topic.                                                                                                           |
| `timezone`           | `Australia/Sydney`           | Your timezone (corrects for daylight saving)                                                                                                                              |
| `section`            | `venturer`                   | The Section you wish to notify. This will be `joey`, `cub`, `scout`, `venturer` or `rover`.                                                                               |
| `meeting_weekday`    | `null`                       | The day of the week on which the bot will send a "No meeting tonight" message if there's no event. Monday is `0`, Sunday is `6`. `null` disables this feature.            |
| `what3words_api_key` | `ABCDEFGH`                   | The API key from what3words. Requests are free and unlimited for this script.                                                                                             |
| `name_replacements`  | `"John Smith": "Fred Smith"` | Replace a full name with another full name. Useful where a person's name in Terrain is not what they are usually called. This affects mentions of Leaders and Assistants. |

## Features

Sends a message (see sample output below) to the youth members' JANDI topic with full event details. 

Sends a message to any parents' topic with concise details.

Makes any what3words addresses clickable and highlights where they are in normal terms. Also highlights when they may be incorrect (i.e. outside Australia)

Only notifies of events starting on the current day in the specified timezone. Due to the way Terrain stores and retrieves events in UTC, there are known issues with this.

There are more, documentation is coming soon...

## Example output

**Upcoming event from Scouts | Terrain**

Bushwalk

📍 Scout Campsite [///sizes.junior.unwell](https://w3w.co/sizes.junior.unwell) (near Merewether Heights, New South Wales)

🕒 9:00 AM - 3:00 PM

🌱 Personal Growth Challenge


A day hike through the bush of Scout Campsite.

**Leader:** John Smith

**Assistants:** James Blue, Amanda White

View on [Scouts | Terrain](terrain.scouts.com.au/programming)

## To-do

- Allow for what3words API bypass
- Allow for parent topic bypass
- Fix issues with overlapping events
- Section also informs `connectColour`