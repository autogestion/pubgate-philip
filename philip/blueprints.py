import os
from pathlib import Path

from sanic import response, Blueprint
from jinja2 import Environment, PackageLoader

from pubgate.db.boxes import Outbox, Inbox

philip_v1 = Blueprint('philip')


philip_dir = os.path.dirname(os.path.abspath(__file__))
philip_v1.static('/static', f'{philip_dir}/static')
parent_dir = Path(philip_dir).parent
philip_v1.static('/svelte_static', f'{parent_dir}/fephilip/public')

jinja_env = Environment(
    loader=PackageLoader("philip", "template"), trim_blocks=True, lstrip_blocks=True
)


@philip_v1.route('/svelte', methods=['GET'])
async def svelte(request, **kwargs):
    return response.html(
            jinja_env.get_template("svelte_home.jinja").render(
                static_url="svelte_static/",
                conf=request.app.config,
        )
    )


@philip_v1.route('/local', methods=['GET'])
@philip_v1.route('/fed', methods=['GET'])
@philip_v1.route('/home', methods=['GET'])
@philip_v1.route('/about', methods=['GET'])
@philip_v1.route('/', methods=['GET'])
async def home(request, **kwargs):
    data = await Outbox.find(filter={
                "deleted": False,
                "activity.type": "Create"
            },
            sort="activity.published desc",
            limit=50)
    posts = Outbox.activity_clean(data.objects, striptags=True)

    feddata = await Inbox.find(filter={
                "deleted": False,
                "activity.type": "Create"
            },
            sort="activity.published desc",
            limit=50)
    fedposts = Inbox.activity_clean(feddata.objects, striptags=True)

    return response.html(
        # html_minify(
            jinja_env.get_template("home.jinja").render(
                static_url="static/",
                conf=request.app.config,
                localposts=posts,
                fedposts=fedposts

            # )
        )
    )


# @app.route("/blog/post/<post>")
# async def blog_post(request, post):
#     post = blog_.find_post(unquote(post))
#
#     return html(
#         html_minify(
#             jinja_env.get_template("blog-post.jinja").render(
#                 static_url=STATIC_URL,
#                 blog_static_url=BLOG_STATIC_URL,
#                 post=post,
#                 rss_url=env.rss_url,
#             )
#         ),
#         status=200 if post else 404,
#     )
#
#
# @app.route("/blog/tag/<tag>")
# async def blog_tag(request, tag):
#     posts = blog_.find_posts_by_tag(unquote(tag))
#
#     return html(
#         html_minify(
#             jinja_env.get_template("blog-tag.jinja").render(
#                 static_url=STATIC_URL, posts=posts, tag=tag
#             )
#         ),
#         status=200 if len(posts) > 0 else 404,
#     )