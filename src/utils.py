import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
import os
import json
import glob
import shutil

# this are combinations of the form example: {{\\'o}}
accents = [
    ["'A", "Á"],
    ["'a", "á"],
    ['"a', "ä"],
    ["^a", "â"],
    ["`a", "à"],
    ["~a", "ã"],
    ["aa", "å"],
    ["'c", "ć"],
    ["'e", "é"],
    ["'E", "É"],
    ['"e', "ë"],
    ["^e", "ê"],
    ["`e", "è"],
    ["'i", "í"],
    ['"i', "ï"],
    ["^i", "î"],
    ["`i", "ì"],
    ["'o", "ó"],
    ['"o', "ö"],
    ['"O', "Ö"],
    ["^o", "ô"],
    ["`o", "ò"],
    ["'u", "ú"],
    ['"u', "ü"],
    ["^u", "û"],
    ["`u", "ù"],
    ['"U', "Ü"],
    ['"u', "ü"],
    ["O", "Ø"],
    ["o", "ø"],
    ["l", "ł"],
    ["'n", "ń"],
    ["L", "Ł"],
    ["l", "ł"],
    ["&", "&amp;"],
    ["'c", "ć"],
    ["~n", "ñ"],
    ["'n", "ń"],
    ["s", "ß"],
]

# this are combinations of the form {\\a{b}}
# where a is the first character and b the second one
accents2 = [
    ["ua", "ă"],
    ["ve", "ě"],
    ["vS", "Š"],
    ["cS", "Ş"],
    ["vs", "š"],
    ["vz", "ž"],
    ["vc", "č"],
    ["vC", "Č"],
    ["cC", "Ç"],
    ["ua", "ă"],
    ["Ho", "ő"],
    ["vZ", "Ž"],
    ["cc", "ç"],
    ["ug", "ğ"],
    [".z", "ż"],
]


def xml_string(text):
    text = text.replace("``", u"“")
    text = text.replace("''", u"”")

    for tex, utf8 in accents:
        # utf8 = utf8.decode('utf-8')
        text = text.replace("{{\\%s}}" % tex, utf8)  # {{\"a}}
        # text = text.replace('\\%s' % tex, utf8)            # \"a
    for tex, utf8 in accents2:
        text = text.replace("{\\%s{%s}}" % tuple(tex), utf8)
    return text

def remove_braces(text):
    text = text.replace("{ ", "")
    text = text.replace(" }", "")
    return text

def authors2string(auth_list):
    auth = ""
    for a in auth_list:
        auth += remove_braces(xml_string(a)) + ", "
    return auth[:-2]
    """Return authors list as a string"""
    template = """@article{JMLR:YYY,
  author  = {%s},
  title   = {XXX},
  journal = {Journal of Machine Learning Research},
  year    = {2016}
  }
"""
    parser = BibTexParser()
    parser.customization = convert_to_unicode
    tmp = template % " and ".join(auth_list)
    bib_database = bibtexparser.loads(tmp, parser=parser)
    return bib_database.entries[0]["author"].replace(" and ", ", ")


def get_info(vol):
    os.chdir("v%s" % vol)
    ids = glob.glob("*/")
    info_list = []
    for paper_id in ids:
        with open("%s/info.json" % paper_id, "r") as fp:
            # some cleanup for the html display
            id_info = json.load(fp)
            id_info["title"] = id_info["title"]
            # some authors write {TeXt} to ensure that its capitalized correctly in latex
            id_info["authors_string"] = authors2string(id_info["authors"])

            id_info["abstract"] = xml_string(id_info["abstract"])
            id_info["authors_bibtex"] = " and ".join(id_info["authors"])
            if "title_html" not in id_info:
                id_info["title_html"] = xml_string(id_info["title"])
            id_info["title_html"] = id_info["title_html"]

            id_info["authors_list"] = [
                xml_string(u.strip()) for u in id_info["authors"]
            ]

        info_list.append(id_info)
    os.chdir("..")
    # sort by issue
    return sorted(info_list, key=lambda k: k["issue"])


def render_paper(info, env, prefix, base_url):
    """render an individual paper"""
    vol = info["volume"]
    id = info["id"]

    papers_dir = os.path.join("output", prefix, "papers")
    with open(os.path.join(papers_dir, "v%s/%s.html" % (vol, id)), "w") as f:

        template = env.get_template("papers/item.html")
        out = template.render(**info, base_url=base_url, papers_active=True)
        f.write(out)
    with open(os.path.join(papers_dir, "v%s/%s.bib" % (vol, id)), "w") as f:
        bib_template = env.get_template("papers/biblio.bib")
        out = bib_template.render(**info)
        f.write(out)
    os.makedirs(os.path.join(papers_dir, "volume%s/%s" % (vol, id)), exist_ok=True)

    # use wildcard to match also other PDFs like erratums
    pdf_files = glob.glob("v%s/%s/*.pdf" % (vol, id))
    # check that there's a file with name $id.pdf
    if not ("%s.pdf" % id) in set([os.path.basename(file) for file in pdf_files]):
        raise ValueError(("%s.pdf not found in folder" % id))
    for file in pdf_files:
        bname = os.path.basename(file)
        shutil.copy(
            "v%s/%s/%s" % (vol, id, bname),
            os.path.join(papers_dir, "volume%s/%s/%s" % (vol, id, bname)),
        )
