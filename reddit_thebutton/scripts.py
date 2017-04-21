from pylons import app_globals as g

from r2.lib.utils import in_chunks
from r2.models import Account, Subreddit
from reddit_thebutton.models import (
    ACCOUNT_CREATION_CUTOFF,
    ButtonActivity
)
from collections import Counter


def update_flair_counts():
    flairs = Counter()
    user_ids = []

    sr = Subreddit._byID(g.live_config["thebutton_srid"], data=True)
    raw = [ba._id36 for ba in ButtonActivity._all()]

    for user_chunk in in_chunks(user_ids, size=100):
        users = Account._byID36(user_chunk, data=True, return_dict=False)
        for user in users:
            flair = user.flair_css_class(sr._id)
            if not flair:
                if user._date < ACCOUNT_CREATION_CUTOFF:
                    flair = "no-press"
                else:
                    flair = "cant-press"

            flairs[flair] += 1

    if 'cheater' in flairs:
        del flairs['cheater']

    sr.flair_counts = sorted(
        flairs.iteritems(),
        key=lambda x: 'z' if x[0] == 'no-press' else x[0],
        reverse=True)
    sr._commit()
