
# general Socsim dictionaries
domains = {"Cyber":0, "CVE":1, "Crypto":2}


# Github events, attributes
github_events_list = ["createevent", "deleteevent", "pullrequestevent", "pullrequestreviewcommentevent", "issuesevent",
               "issuecommentevent", "pushevent", "commitcommentevent","watchevent", "forkevent", "gollumevent",
               "publicevent", "releaseevent", "memberevent"]
github_events = {"createevent":0, "deleteevent":1, "pullrequestevent":2, "pullrequestceviewcommentevent":3,
                       "issuesevent":4, "issuecommentevent":5, "pushevent":6, "commitcommentevent":7, "watchevent":8,
                       "forkevent":9, "gollumevent":10, "publicevent":11, "releaseevent":12, "memberevent":13}

github_action_subtypes_list = ["open", "close", "reopen", "repo", "branch", "tag"]

github_action_subtypes = {"open":0, "close":1, "reopen":2, "repo":3, "branch":4, "tag":5}

# Twitter
twitter_events_list = ["retweet", "reply", "tweet", "quotedtweet"]
twitter_events = {"retweet":0, "reply":1, "tweet":2, "quotedtweet":3}

# Reddit
reddit_events_list = ["post", "comment"]
reddit_events = {"post":0, "comment":1}
