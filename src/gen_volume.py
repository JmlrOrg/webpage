import os
import sys
from jinja2 import Environment, FileSystemLoader, select_autoescape

import utils

# only build the new website
PREFIXES = ("beta", "")


vol = sys.argv[1]

for prefix in PREFIXES:
    os.makedirs(os.path.join("output", prefix, "papers/v%s" % vol), exist_ok=True)

    env = Environment(
        loader=FileSystemLoader("templates/" + prefix),
        autoescape=select_autoescape(["html", "xml"]),
    )

    if prefix == "":
        base_url = ""
    else:
        base_url = "/" + prefix

    # render the individual papers
    info_list = utils.get_info(vol)
    for info in info_list:
        utils.process(info, env, prefix, base_url)

    # render volume html file
    with open(os.path.join("output", prefix, "papers/v%s/index.html" % vol), "w") as f:
        volume_template = env.get_template("papers/volume.html")
        out = volume_template.render(info_list=info_list, vol=vol, base_url=base_url, papers_active=True)
        f.write(out)
    with open(os.path.join("output", prefix, "papers/index.html"), "w") as f:
        editorial_board_template = env.get_template("papers/index.html")
        out = editorial_board_template.render(
            info_list=info_list, volume=vol, base_url=base_url, papers_active=True,
        )
        f.write(out)

    # rss feed
    with open(os.path.join("output", prefix, "jmlr.xml"), "w") as f:
        # sort by issue
        info_by_issue = sorted(info_list, key=lambda k: k["issue"])[::-1]
        editorial_board_template = env.get_template("jmlr.xml")
        out = editorial_board_template.render(
            info_list=info_by_issue, vol=vol, base_url=base_url
        )
        f.write(out)
