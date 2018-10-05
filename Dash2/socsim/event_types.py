
# general Socsim dictionaries
domains = {"Cyber":0, "CVE":1, "Crypto":2}


# Github events, attributes
github_events_list = ["CreateEvent", "DeleteEvent", "PullRequestEvent", "PullRequestReviewCommentEvent", "IssuesEvent",
               "IssueCommentEvent", "PushEvent", "CommitCommentEvent","WatchEvent", "ForkEvent", "GollumEvent",
               "PublicEvent", "ReleaseEvent", "MemberEvent"]
github_events = {"CreateEvent":0, "DeleteEvent":1, "PullRequestEvent":2, "PullRequestReviewCommentEvent":3,
                       "IssuesEvent":4, "IssueCommentEvent":5, "PushEvent":6, "CommitCommentEvent":7, "WatchEvent":8,
                       "ForkEvent":9, "GollumEvent":10, "PublicEvent":11, "ReleaseEvent":12, "MemberEvent":13}

github_action_subtypes_list = ["open", "close", "reopen", "repo", "branch", "tag"]

github_action_subtypes = {"open":0, "close":1, "reopen":2, "repo":3, "branch":4, "tag":5}

# Twitter
twitter_events_list = ["RT", "Reply", "Tweet", "QuotedTweet"]
twitter_events = {"RT":0, "Reply":1, "Tweet":2, "QuotedTweet":3}

# Reddit
reddit_events_list = ["Post", "Comment"]
reddit_events = {"Post":0, "Comment":1}
