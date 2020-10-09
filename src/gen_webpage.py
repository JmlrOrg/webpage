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


def render_webpage(env, prefix, page, base_url):
    with open(os.path.join("output", prefix, page), "w") as f:
        template = env.get_template(page)
        out = template.render(
            **info,
            year=YEAR,
            base_url=base_url,
            home_active=(page == "index.html"),
            editorial_board_active=(page == "editorial-board.html"),
            stats_active=(page == "stats.html")
        )
        f.write(out)


if __name__ == "__main__":

    # .. current webpage ..
    for prefix in ["", "beta"]:
        if not os.path.exists(os.path.join("output", prefix)):
            os.mkdir(os.path.join("output", prefix))

        if prefix == "":
            base_url = ""
        else:
            base_url = "/" + prefix
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
            render_webpage(env, prefix, page, base_url)

        # MLOSS webpage
        mloss_dir = os.path.join("output", prefix, "mloss")
        if not os.path.exists(mloss_dir):
            os.mkdir(mloss_dir)

        render_webpage(env, prefix, "mloss/mloss-info.html", base_url)
        with open(os.path.join("output", prefix, "mloss/index.html"), "w") as f:
            mloss_start_vol = 11
            list_info_mloss = []
            while True:
                # get all info for v18 and onwards
                try:
                    info_list = utils.get_info(mloss_start_vol)
                    info_mloss = filter(
                        lambda x: x.get("special_issue", "") == "MLOSS", info_list
                    )
                    list_info_mloss.append(info_mloss)
                    mloss_start_vol += 1
                except FileNotFoundError:
                    break

            mloss_template = env.get_template("mloss/index.html")
            out = mloss_template.render(
                list_info_mloss=list_info_mloss, base_url=base_url
                mloss_active=True
            )
            f.write(out)

        # topic_dir = os.path.join("output", prefix, "topic")
        # if not os.path.exists(topic_dir):
        #     os.mkdir(topic_dir)

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
        
