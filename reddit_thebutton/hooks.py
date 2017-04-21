from pylons import app_globals as g
from pylons import tmpl_context as c

from r2.config import feature
from r2.lib import websockets
from r2.lib.hooks import HookRegistrar
from r2.lib.pages import SideBox
from r2.models import Subreddit, NotFound

from reddit_thebutton.pages import TheButton
from reddit_thebutton.models import ButtonActivity

hooks = HookRegistrar()


@hooks.on("hot.get_content")
def add_thebutton(controller):
    if getattr(c.site, '_id', None) == g.live_config["thebutton_srid"]:
        return TheButton()


@hooks.on('js_config')
def add_js_config(config):
    if getattr(c.site, '_id', None) == g.live_config["thebutton_srid"]:
        config['thebutton_websocket'] = websockets.make_url("/thebutton",
                                                            max_age=24 * 60 * 60)


@hooks.on('home.add_sidebox')
def add_home_sidebox():
    if not feature.is_enabled('thebutton_on_homepage'):
        return None

    try:
        sr = Subreddit._byID(
            g.live_config["thebutton_srid"], data=True, stale=True)
    except NotFound:
        return None

    return SideBox(
        title="Did you press the button?",
        css_class="thebutton_sidebox",
        link="/r/%s" % sr.name,
        target="_blank",
    )

@hooks.on('plugins.set_up_user_context')
def record_activity():
    return ButtonActivity._create(user=c.user)
