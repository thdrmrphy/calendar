# Pathfinder

## A Jandi-Terrain webhook integration
**Do you use Jandi for your Scouting communications?**

**Do you have a Scouts | Terrain account?**

**Do you have a server to run Python scripts on?**

**If you said yes to all three, you're in the right place.**

If you didn't, but you know what you're doing, you can probably hack something together.

Anyway, what's Pathfinder? It's a Python script that checks your Terrain calendar for events in your unit on the current day and, if there's something, it'll post information to Jandi via a webhook. Additionally, by specifying your weekly meeting day (such as Thursday, the default), the bot can confirm if there is no event in Terrain to users on Jandi.

## Dependencies

```
requests
json
datetime
pytz
re
what3words
```

## Variables

`terrain_username` is your state, then a hyphen, then your member number. For example, `nsw-1234567`.

`terrain_password` is your password for Terrain.

`wh_url` is the URL you got for the webhook you set up in Jandi.

`timezone` is your timezone (corrects for daylight saving). Default is Sydney.

The weekday in line 108 starts at 0 (Monday) and goes to  (Sunday). This is the day on which the bot will tell you there's no meeting (if there should be one but isn't).

The what3words API key in line 184 lets you use the what3words API to convert w3w addresses into clickable links (with a confirmation of the rough area).

## Features

Run the script every day at a designated time (use a cronjob like `0 9 * * *`)

The webhook post includes the event title, location (converts any what3words locations to a clickable link), start/finish time, challenge area, description, and Leaders/Assistants.

On the designated weekday, if there is no regular meeting, the bot will communicate this.

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