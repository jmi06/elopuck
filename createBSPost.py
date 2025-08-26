import requests
import json
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
# import tweepy
import time
load_dotenv()

BLUESKY_HANDLE = os.getenv('BLUESKY_USERNAME')
BLUESKY_PASSWORD = os.getenv('BLUESKY_PASSWORD')


# TW_CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
# TW_CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
# TW_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
# TW_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')



def create_post():
    global mlb_team_hashtags
        
    mlb_team_hashtags = {
        "Anaheim Ducks": "#FlyTogether",
        "Arizona Coyotes": "#Yotes",
        "Boston Bruins": "#NHLBruins",
        "Buffalo Sabres": "#LetsGoBuffalo",
        "Calgary Flames": "#Flames",
        "Carolina Hurricanes": "#CauseChaos",
        "Chicago Blackhawks": "#Blackhawks",
        "Colorado Avalanche": "#GoAvsGo",
        "Columbus Blue Jackets": "#CBJ",
        "Dallas Stars": "#TexasHockey",
        "Detroit Red Wings": "#LGRW",
        "Edmonton Oilers": "#LetsGoOilers",
        "Florida Panthers": "#TimeToHunt",
        "Los Angeles Kings": "#GoKingsGo",
        "Minnesota Wild": "#MNWild",
        "Montreal Canadiens": "#GoHabsGo",
        "Nashville Predators": "#Preds",
        "New Jersey Devils": "#NJDevils",
        "New York Islanders": "#Isles",
        "New York Rangers": "#NYR",
        "Ottawa Senators": "#GoSensGo",
        "Philadelphia Flyers": "#LetsGoFlyers",
        "Pittsburgh Penguins": "#LetsGoPens",
        "San Jose Sharks": "#SJSharks",
        "Seattle Kraken": "#SeaKraken",
        "St. Louis Blues": "#STLBlues",
        "Tampa Bay Lightning": "#GoBolts",
        "Toronto Maple Leafs": "#LeafsForever",
        "Vancouver Canucks": "#Canucks",
        "Vegas Golden Knights": "#VegasBorn",
        "Washington Capitals": "#ALLCAPS",
        "Winnipeg Jets": "#GoJetsGo",
    }





    # Using a trailing "Z" is preferred over the "+00:00" format
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


    postNow = datetime.now()


    formatted_time = postNow.strftime("%I:%M %p")




    resp = requests.post(

        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": BLUESKY_HANDLE, "password": BLUESKY_PASSWORD},

    )

    session = resp.json()

    accessJwt = session["accessJwt"]



    with open('post.png', "rb") as f:
        img_bytes = f.read()

    if len(img_bytes) > 1000000:
        raise Exception(
            f"image file size too large. 1000000 bytes maximum, got: {len(img_bytes)}"
        )


    resp = requests.post(
        "https://bsky.social/xrpc/com.atproto.repo.uploadBlob",
        headers={
            "Content-Type": 'image/png',
            "Authorization": "Bearer " + session["accessJwt"],
        },
        data=img_bytes,
    )


    blob = resp.json()["blob"]






    postinfo = {}
    with open('post.json') as postfile:
        postinfo = json.load(postfile)

    posttext = f"NHL EloPuck Update as of {formatted_time}: \n{postinfo['winning_team']} beat {postinfo['losing_team']} {postinfo['score']} \nSee more at https://elopuck.pages.dev/ \n#NHL"
    posttextX = f"NHL EloPuck Update as of {formatted_time}: \n{postinfo['winning_team']} beat {postinfo['losing_team']} {postinfo['score']} \nSee more at https://elopuck.pages.dev/ \n#NHL\n{mlb_team_hashtags[postinfo['winning_team']]}\n{mlb_team_hashtags[postinfo['losing_team']]}"


    facets = [
        {
            "index": {
                "byteStart": posttext.find("https://elopuck.pages.dev/"),
                "byteEnd": posttext.find("https://elopuck.pages.dev/") + len("https://elopuck.pages.dev/")
            },
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": "https://elopuck.pages.dev/"}]
        },
        {
            "index": {
                "byteStart": posttext.find("#NHL"),
                "byteEnd": posttext.find("#NHL") + len("#NHL")
            },
            "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": "NHL"}]
        }
    ]










    post = {
        "$type": "app.bsky.feed.post",
        "text": posttext,
        "createdAt": now,
        'facets': facets
    }




    

    post["embed"] = {
        "$type": "app.bsky.embed.images",
        "images": [{
            "alt": "",
            "image": blob,
            "aspectRatio": {"width": 313, "height": 236}
        }],
    }


    resp = requests.post(
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": "Bearer " + session["accessJwt"]},
        json={
            "repo": session["did"],
            "collection": "app.bsky.feed.post",
            "record": post,
        },
    )

    print('posted to bluesky')
    # twitter_post()


# def twitter_post():


#     # Using a trailing "Z" is preferred over the "+00:00" format
#     now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


#     postNow = datetime.now()


#     formatted_time = postNow.strftime("%I:%M %p")




#     with open('post.json') as postfile:
#         postinfo = json.load(postfile)

#     posttext = f"NHL EloPuck Update as of {formatted_time}: \n{postinfo['winning_team']} beat {postinfo['losing_team']} {postinfo['score']} \nSee more at https://eloball.pages.dev/ \n#MLB"
#     posttextX = f"NHL EloPuck Update as of {formatted_time}: \n{postinfo['winning_team']} beat {postinfo['losing_team']} {postinfo['score']} \nSee more at https://elopuck.pages.dev/ \n#MLB\n{mlb_team_hashtags[postinfo['winning_team']]}\n{mlb_team_hashtags[postinfo['losing_team']]}"




#     try:
#          client = tweepy.Client(
#              consumer_key= TW_CONSUMER_KEY,
#              consumer_secret= TW_CONSUMER_SECRET,
#              access_token = TW_ACCESS_TOKEN,
#              access_token_secret= TW_ACCESS_SECRET
#          )


#          auth = tweepy.OAuth1UserHandler(TW_CONSUMER_KEY, TW_CONSUMER_SECRET, TW_ACCESS_TOKEN, TW_ACCESS_SECRET)
#          api_v1 = tweepy.API(auth)
#          media = api_v1.media_upload("post.png")


#          response = client.create_tweet(
#                  text=posttextX,
#                  media_ids=[media.media_id]
#          )
#     except:
#          print('twitter is beefing with us rn')
#          time.sleep(30)
#          twitter_post()








