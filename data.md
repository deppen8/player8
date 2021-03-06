---
layout: page
title: data
subtitle: notes on the dataset
use-site-title: true
---
After every Arsenal match, [Arseblog](https://news.arseblog.com/category/players/player-ratings/) <sup>[<a href="#n1">1</a>]</sup> posts ratings using the common 0-10 scale <sup>[<a href="#n2">2</a>]</sup> for all the Arsenal players who appeared in the match. Beginning in January 2014, Arseblog added the option for readers to submit their own ratings. The averages of these fan ratings are published alongside the author's ratings.

Arseblog has published player ratings like this for over 200 Arsenal matches, so there are more than 3,000 documented player appearances, each with two associated ratings: one from Arseblog, one from the fans.

Arseblog.com has a dedicated section for all of the [Player Ratings](https://news.arseblog.com/category/players/player-ratings/) posts. Each of these posts is formatted in similar ways, so I was able to write a Python web scraper script that, given the URL of the specific page, extracts the following information:
- For each player that appeared in the match:
    - Player name (`name`)
    - Arseblog rating (`arseblograting`)
    - User rating (`userrating`)
- General match info:
    - Date (`date`)
    - Competition (`competition`)
    - Opponent (`opponent`)
    - Arsenal goals (`arsegoals`)
    - Opponent goals (`oppgoals`)

From this information, I easily derived the Season (`season`) and whether the match was Home or Away (`home_away`).
This information was stored in an SQLite database with the schema:

![database schema](/img/db_schema.png)

I have since manually added the following info to the players table:
- Shirt number (`number`)
- Primary positions (`positions`)
- National team (`natl_team`)
- Birthdate (`birthdate`)
- Academy graduate? (`academy_grad`)
- Nickname (`nickname`)
- Less common positions (`rare_positions`)

# Caveats
There are some minimal data checks built into the scraper code, but, in general, the data has not been thoroughly scrubbed or validated with any other sources; there could be errors anywhere. That said, here some places where you might expect to find errors or deviations from expectations, in no particular order:
- The dataset begins in the middle of the 2013-14 season. More specifically, it starts with the first game of 2014, a 2-0 FA Cup victory over Spurs. This is when Arseblog began incorporating ratings from readers.
- I have not accounted for neutral site games in the `home_away` field. The FA Cup finals at Wembley, for instance, are all recorded as home games.
- Some team names may appear in different forms. For example, games against Hull City might be recorded as "Hull" or "Hull City". I have done some checks of this, but no guarantees.
- Player numbers, national teams, and birthdates are based on information from [transfermarkt.co.uk](https://www.transfermarkt.co.uk/fc-arsenal/startseite/verein/11/saison_id/2017).
- For players that wore more than one number at Arsenal, I have recorded the most recent number they've worn or the last number they wore before leaving the club. For example, Alexis Sanchez is associated with number 7, not 17.
- Player positions are assigned mostly from memory, so are open to interpretation. For some young players who made few appearances for the first team (and often not in their natural preferred position), I used the positions defined for them on transfermarkt.co.uk.
- Here is how I conceived of the difference between `positions` and `rare_positions`: `rare_positions` are `positions` where a player might have played but it would be a surprise to see them starting there on the teamsheet.
- I have not confirmed that all Arsenal matches are included in the database. I am relying on the assumption that all games where Arseblog did ratings are included under the [Player Ratings](https://news.arseblog.com/category/players/player-ratings/) section of the website. I have discovered that the following matches do not have ratings associated with them:
    - 19 August, 2017, Stoke 1 - 0 Arsenal

### Notes
<a name="n1">[1]</a> I am deeply grateful to Andrew Mangan and the rest of the Arseblog.com team for allowing me to use this data. You can support their work at <a href="https://www.patreon.com/arseblog" target="_blank">patreon.com/arseblog</a>.

<a name="n2">[2]</a> See <a href="http://www.slate.com/articles/sports/sports_nut/2011/09/lionel_messi_goes_to_11.html" target="_blank">this article from Slate</a> for a quick history of 0-10 player ratings. It also does well to recognize the wild subjectivity of a single person's rankings while still arguing for their utility.
