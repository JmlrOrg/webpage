import json
import os
from datetime import datetime
from glob import glob
from jinja2 import Environment, FileSystemLoader, select_autoescape
import utils


YEAR = datetime.today().year


editorial_board_info = json.load(open("editorial-board.json", "r"))

if not os.path.exists("output"):
    os.mkdir("output")


def render_webpage(env, prefix, page, base_url, template_kw):
    with open(os.path.join("output", prefix, page), "w") as f:
        template = env.get_template(page)
        out = template.render(
            **template_kw,
            year=YEAR,
            base_url=base_url,
            home_active=(page == "index.html"),
            editorial_board_active=(page == "editorial-board.html"),
            stats_active=(page == "stats.html")
        )
        f.write(out)


if __name__ == "__main__":

    for prefix in ["", "beta"]:
        if not os.path.exists(os.path.join("output", prefix)):
            os.mkdir(os.path.join("output", prefix))

        if prefix == "":
            base_url = ""
        else:
            base_url = "/" + prefix

        # .. MLOSS webpage ..
        mloss_dir = os.path.join("output", prefix, "mloss")
        if not os.path.exists(mloss_dir):
            os.mkdir(mloss_dir)

        env = Environment(
            loader=FileSystemLoader(os.path.join("templates", prefix)),
            autoescape=select_autoescape(["html", "xml"]),
        )
        render_webpage(env, prefix, "mloss/mloss-info.html", base_url, editorial_board_info)
        with open(os.path.join("output", prefix, "mloss/index.html"), "w") as f:
            mloss_start_vol = 11
            list_info_mloss = []
            while True:
                # get all info for v11 and onwards
                try:
                    # reverse by-issue sorting
                    info_list = utils.get_info(mloss_start_vol)[::-1]
                    info_mloss = filter(
                        lambda x: x.get("special_issue", "") == "MLOSS", info_list
                    )
                    list_info_mloss.append(info_mloss)
                    mloss_start_vol += 1
                except FileNotFoundError:
                    break

            mloss_template = env.get_template("mloss/index.html")
            out = mloss_template.render(
                list_info_mloss=list_info_mloss, base_url=base_url,
                mloss_active=True
            )
            f.write(out)


        for (special_topic, template) in [("Bayesian Optimization", "bayesian_optimization.html")]:
            topic_dir = os.path.join("output", prefix, "papers/topic")
            if not os.path.exists(topic_dir):
                os.makedirs(topic_dir, exist_ok=True)

            with open(os.path.join("output", prefix, "papers/topic/%s" % template), "w") as f:
                topic_start_vol = 11
                list_info_topic = []
                while True:
                    # get all info for v18 and onwards
                    try:
                        info_list = utils.get_info(topic_start_vol)
                        info_topic = filter(
                            lambda x: x.get("special_issue", "") == special_topic, info_list
                        )
                        list_info_topic.append(info_topic)
                        topic_start_vol += 1
                    except FileNotFoundError:
                        break
                topic_template = env.get_template("papers/topic/%s" % template)
                out = topic_template.render(
                    list_info_topic=list_info_topic, base_url=base_url
                )
                f.write(out)

        # .. build volumes one by one ...
        volumes = sorted([int(v[1:]) for v in  glob("v*")])
        for vol in volumes:
            print("Generating Volume %s out of %s" % (vol, volumes[-1]))
            os.makedirs(os.path.join("output", prefix, "papers/v%s" % vol), exist_ok=True)

            # render the individual papers
            info_list = utils.get_info(vol)
            for paper_info in info_list:
                utils.process(paper_info, env, prefix, base_url)

            # render volume html file
            with open(os.path.join("output", prefix, "papers/v%s/index.html" % vol), "w") as f:
                volume_template = env.get_template("papers/volume.html")
                out = volume_template.render(info_list=info_list, vol=vol, base_url=base_url, papers_active=True)
                f.write(out)
            with open(os.path.join("output", prefix, "papers/index.html"), "w") as f:
                papers_index_template = env.get_template("papers/index.html")
                out = papers_index_template.render(
                    info_list=info_list, volume=vol, base_url=base_url, papers_active=True,
                )
                f.write(out)

            # rss feed
            with open(os.path.join("output", prefix, "jmlr.xml"), "w") as f:
                # sort by issue
                info_by_issue = sorted(info_list, key=lambda k: k["issue"])[::-1]
                rss_template = env.get_template("jmlr.xml")
                out = rss_template.render(
                    info_list=info_by_issue, vol=vol, base_url=base_url
                )
                f.write(out)

        render_webpage(env, prefix, "index.html", base_url, {'info_list': info_list[-20:]})
        for page in [
                "author-info.html",
                "contact.html",
                "editorial-board.html",
                "editorial-board-reviewers.html",
                "news.html",
                "reviewer-guide.html",
                "stats.html",
                "faq.html",
        ]:
            render_webpage(env, prefix, page, base_url, editorial_board_info)

