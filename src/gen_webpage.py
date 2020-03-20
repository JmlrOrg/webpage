import json
import utils
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape


YEAR = datetime.today().year
# TODO detect if we are in the bin directory and go down one step

info = json.load(open("editorial-board.json", "r"))

if not os.path.exists("output"):
    os.mkdir("output")


def render_webpage(prefix, page):
    if not os.path.exists(os.path.join("output", prefix)):
        os.mkdir(os.path.join("output", prefix))
    with open(os.path.join("output", prefix, page), "w") as f:
        t_path = os.path.join(prefix, "%s" % page)
        template = env.get_template(t_path)
        out = template.render(**info, year=YEAR)
        f.write(out)


# .. beta webpage ..
prefix = "beta"
if not os.path.exists(os.path.join("output", prefix)):
    os.mkdir(os.path.join("output", prefix))
env = Environment(
    loader=FileSystemLoader(os.path.join("templates", "beta")),
    autoescape=select_autoescape(["html", "xml"]),
)

for page in [
    "index.html",
    "editorial-board.html",
    "news.html",
    "author-info.html",
    "contact.html",
    "editorial-board-reviewers.html",
]:
    base_url = "/" + prefix
    with open(os.path.join("output", prefix, page), "w") as f:
        template = env.get_template("%s" % page)
        out = template.render(**info, year=YEAR, base_url=base_url, home_active=(page == "index.html"))
        f.write(out)
# .. end beta webpage ..

# .. current webpage ..
prefix = ""
base_url = prefix
env = Environment(
    loader=FileSystemLoader(os.path.join("templates", prefix)),
    autoescape=select_autoescape(["html", "xml"]),
)


for page in [
    "author-info.html",
    "contact.html",
    "editorial-board.html",
    "editorial-board-reviewers.html",
    "news.html",
    "index.html",
    "reviewer-guide.html",
    "stats.html",
]:
    render_webpage(prefix, page)

# MLOSS webpage
if not os.path.exists("output/mloss/"):
    os.mkdir("output/mloss/")

render_webpage("", "mloss/mloss-info.html")
with open(os.path.join("output", prefix, "mloss/index.html"), "w") as f:
    vol = 18
    list_info_mloss = []
    while True:
        # get all info for v18 and onwards
        try:
            info_list = utils.get_info(vol)
            info_mloss = filter(
                lambda x: x.get("special_issue", "") == "MLOSS", info_list
            )
            list_info_mloss.append(info_mloss)
            vol += 1
        except FileNotFoundError:
            break

    editorial_board_template = env.get_template("mloss/index.html")
    out = editorial_board_template.render(
        list_info_mloss=list_info_mloss, base_url=base_url
    )
    f.write(out)
