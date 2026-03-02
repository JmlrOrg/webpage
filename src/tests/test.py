import pytest
import glob
import json
import filecmp
from functools import lru_cache
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

all_volumes = sorted([int(v[1:]) for v in glob.glob("v*")])

PREFIXES = ["/", "/beta/"]
BIBTEX_PREFIXES = ["/"]
if not filecmp.cmp("templates/papers/biblio.bib", "templates/beta/papers/biblio.bib", shallow=False):
    BIBTEX_PREFIXES = PREFIXES


def test_xml_string():
    t = r"\mathcal{O}"
    assert utils.xml_string(t) == t


def test_abstract_html_validator_allows_safe_markup():
    utils.validate_abstract_html(
        "A safe abstract with <i>markup</i> and math $0 \\lt s \\lt 1$.",
        "test-paper",
    )


def test_abstract_html_validator_rejects_raw_lt_without_spacing():
    with pytest.raises(ValueError):
        utils.validate_abstract_html("This breaks HTML: $0<s<1$.", "test-paper")


def test_volumes_exist():
    # check that there's a volume directory
    for i in range(6, 26):
        assert os.path.exists(f"output/papers/volume{i}/")

@lru_cache(maxsize=None)
def paper_ids(volume):
    paper_dirs = sorted(glob.glob(f"v{volume}/*/"))
    return tuple([paper_dir.split("/")[1] for paper_dir in paper_dirs])


@lru_cache(maxsize=None)
def load_info(volume, paper_id):
    with open(f"v{volume}/{paper_id}/info.json", "r") as json_file:
        return json.load(json_file)


@lru_cache(maxsize=None)
def load_soup(volume, prefix, paper_id):
    with open(f"output{prefix}papers/v{volume}/{paper_id}.html") as html_file:
        html = html_file.read()
    return BeautifulSoup(html, "html.parser")


def paper_iterator(volume, prefix):
    for paper_id in paper_ids(volume):
        soup = load_soup(volume, prefix, paper_id)
        info = load_info(volume, paper_id)
        yield paper_id, soup, info


@pytest.mark.parametrize("volume", all_volumes)
def test_paper_json(volume):
    # check that json info file has all necessary fields
    for paper_id in paper_ids(volume):
        info = load_info(volume, paper_id)
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
        if volume >= utils.ABSTRACT_HTML_CHECK_MIN_VOLUME:
            utils.validate_abstract_html(info["abstract"], f"v{volume}/{paper_id}")


@pytest.mark.parametrize("volume", all_volumes)
def test_paper_title(volume, prefix="/beta/"):
    for _, soup, info in paper_iterator(volume, prefix):
        if "title_html" in info.keys():
            assert soup.title.string == info["title_html"]
        else:
            assert soup.title.string == utils.xml_string(info["title"])


@pytest.mark.parametrize("volume", all_volumes)
@pytest.mark.parametrize("prefix", PREFIXES)
def test_paper_metadata(volume, prefix):
    for _, soup, info in paper_iterator(volume, prefix):
        citation_title = soup.find_all(attrs={"name": "citation_title"})
        assert len(citation_title) == 1
        if "title_html" in info.keys():
            assert citation_title[0]["content"] == info["title_html"]
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
        set_authors = set([utils.author_string(c) for c in info["authors"]])

        assert citation_authors == set_authors


@pytest.mark.parametrize("volume", all_volumes)
@pytest.mark.parametrize("prefix", BIBTEX_PREFIXES)
def test_paper_bibtex(volume, prefix):
    """Check that authors coincide with the bibtex"""
    for paper_id in paper_ids(volume):
        info = load_info(volume, paper_id)
        set_authors = set([utils.author_string(c) for c in info['authors']])

        parser = BibTexParser()
        out_bib = 'output' + prefix + 'papers/v%s/%s.bib' % (volume, info['id'])
        with open(out_bib) as f:
            bib_database = bibtexparser.load(f, parser=parser)
        authors_bib = set([utils.author_string(u.strip()) for u in bib_database.entries[0]['author'].split(' and ')])

        assert authors_bib == set_authors


@pytest.mark.parametrize("volume", all_volumes)
def test_pdf_exists(volume, prefix="/beta/"):
    for _, soup, info in paper_iterator(volume, prefix):
        citation_pdf = soup.find_all(attrs={"name": "citation_pdf_url"})
        assert len(citation_pdf) == 1
        citation_pdf = citation_pdf[0]["content"]

        citation_pdf2 = soup.find_all(id="pdf")
        assert len(citation_pdf2) == 1
        citation_pdf2 = citation_pdf2[0]["href"]

        assert 'http://jmlr.org' + citation_pdf2 == citation_pdf


@pytest.mark.parametrize("volume", all_volumes)
def test_issue_number(volume):
    all_issues = []
    for paper_id in paper_ids(volume):
        info = load_info(volume, paper_id)
        all_issues.append(info)
    all_issues = sorted(all_issues, key=lambda k: k["issue"])

    # check that the volume has all consecutive issue
    # numbers
    for i in range(len(all_issues)):
        assert all_issues[i]["issue"] == i + 1


def test_xmlstring():
    assert utils.xml_string("Tak{{\\'a}}{\\v{c}}") == "Takáč"
    assert utils.xml_string('Wa{\\"i}ss') == "Waïss"
    assert utils.xml_string("J{\\'e}r{\\^o}me") == "Jérôme"
    assert utils.xml_string('na\\"ive') == "naïve"
    assert utils.xml_string("Fr\\'echet") == "Fréchet"
    assert utils.author_string("Emilija Perkovi\\'c") == "Emilija Perković"
    assert (
        utils.xml_string("Mar{{\\'i}}a del Carmen Rodr{{\\'i}}guez-Hern{{\\'a}}ndez")
        == "María del Carmen Rodríguez-Hernández"
    )
