import pytest
import glob
import json
from bs4 import BeautifulSoup

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode


# local imports
import sys
import os

curpath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, curpath + "/../")
import utils

all_volumes = [int(v[1:]) for v in glob.glob("v*")]

PREFIXES = ["/", "/beta/"]


def test_xml_string():
    t = r"\mathcal{O}"
    assert utils.xml_string(t) == t


def test_volumes_exist():
    # check that there's a volume directory
    for i in range(6, 26):
        assert os.path.exists(f"output/papers/volume{i}/")

def paper_iterator(volume, prefix):
    paper_dirs = glob.glob(f"v{volume}/*/")
    for paper_dir in paper_dirs:
        paper_id = paper_dir.split("/")[1]
        with open(f"output{prefix}papers/v{volume}/{paper_id}.html") as html_file:
            html = html_file.read()
        soup = BeautifulSoup(html, "html.parser")
        with open(f"{paper_dir}/info.json", "r") as json_file:
            info = json.load(json_file)
        yield soup, info


@pytest.mark.parametrize("volume", all_volumes)
@pytest.mark.parametrize("prefix", PREFIXES)
def test_paper_json(volume, prefix):
    # check that json info file has all necessary fields
    for soup, info in paper_iterator(volume, prefix):
        for attr in [
            "abstract",
            "authors",
            "id",
            "issue",
            "pages",
            "title",
            "volume",
            "year",
        ]:
            assert attr in info.keys()
        if "special_issue" in info.keys():
            if info["special_issue"] == "MLOSS":
                fields = [u[0] for u in info["extra_links"]]
                # make sure that there's a code in the extra links
                assert "code" in fields


@pytest.mark.parametrize("volume", all_volumes)
def test_paper_title(volume, prefix="/beta/"):
    for soup, info in paper_iterator(volume, prefix):
        if "title_html" in info.keys():
            assert soup.title.string == info["title_html"]
        else:
            assert soup.title.string == utils.xml_string(info["title"])


@pytest.mark.parametrize("volume", all_volumes)
@pytest.mark.parametrize("prefix", PREFIXES)
def test_paper_metadata(volume, prefix):
    for soup, info in paper_iterator(volume, prefix):
        citation_title = soup.find_all(attrs={"name": "citation_title"})
        assert len(citation_title) == 1
        if "title_html" in info.keys():
            citation_title[0]["content"] == info["title_html"]
        else:
            assert citation_title[0]["content"] == utils.xml_string(info["title"])

        citation_journal = soup.find_all(attrs={"name": "citation_journal_title"})
        assert len(citation_journal) == 1
        assert citation_journal[0]["content"] == "Journal of Machine Learning Research"

        citation_issn = soup.find_all(attrs={"name": "citation_issn"})
        assert len(citation_issn) == 1
        assert citation_issn[0]["content"] == "1533-7928"

        citation_authors = soup.find_all(attrs={"name": "citation_author"})
        citation_authors = set([c["content"] for c in citation_authors])
        set_authors = set([utils.xml_string(c) for c in info["authors"]])

        assert citation_authors == set_authors


@pytest.mark.parametrize("volume", all_volumes)
@pytest.mark.parametrize("prefix", PREFIXES)
def test_paper_bibtex(volume, prefix):
    """Check that authors coincide with the bibtex"""
    for soup, info in paper_iterator(volume, prefix):
        set_authors = set([utils.xml_string(c) for c in info['authors']])

        parser = BibTexParser()
        out_bib = 'output' + prefix + 'papers/v%s/%s.bib' % (volume, info['id'])
        with open(out_bib) as f:
            bib_database = bibtexparser.load(f, parser=parser)
        authors_bib = set([utils.xml_string(u.strip()) for u in bib_database.entries[0]['author'].split(' and ')])

        assert authors_bib == set_authors


@pytest.mark.parametrize("volume", all_volumes)
def test_pdf_exists(volume, prefix="/beta/"):
    for soup, info in paper_iterator(volume, prefix):
        citation_pdf = soup.find_all(attrs={"name": "citation_pdf_url"})
        assert len(citation_pdf) == 1
        citation_pdf = citation_pdf[0]["content"]

        citation_pdf2 = soup.find_all(id="pdf")
        assert len(citation_pdf2) == 1
        citation_pdf2 = citation_pdf2[0]["href"]

        assert 'http://jmlr.org' + citation_pdf2 == citation_pdf


@pytest.mark.parametrize("volume", all_volumes)
@pytest.mark.parametrize("prefix", PREFIXES)
def test_issue_number(volume, prefix):
    all_issues = []
    for soup, info in paper_iterator(volume, prefix):
        all_issues.append(info)
    all_issues = sorted(all_issues, key=lambda k: k["issue"])

    # check that the volume has all consecutive issue
    # numbers
    for i in range(len(all_issues)):
        assert all_issues[i]["issue"] == i + 1


def test_xmlstring():
    assert utils.xml_string("Tak{{\\'a}}{\\v{c}}") == "Takáč"
    assert (
        utils.xml_string("Mar{{\\'i}}a del Carmen Rodr{{\\'i}}guez-Hern{{\\'a}}ndez")
        == "María del Carmen Rodríguez-Hernández"
    )
