import pytest
from article.records.api import ArticleRecord
from invenio_access.permissions import system_identity
from invenio_vocabularies.records.api import Vocabulary


def test_language_reference(
    app, db, lang_type, lang_data, vocabulary_service, article_service, vocab_cf
):
    vocabulary_service.create(system_identity, lang_data)
    Vocabulary.index.refresh()

    article = article_service.create(
        system_identity, {"metadata": {"title": "blah", "language": {"id": "eng"}}}
    )

    assert article.data["metadata"]["language"]["title"] == {
        "en": "English",
        "da": "Engelsk",
    }


def test_affiliation_hierarchy(
    app, db, affiliation_type, vocabulary_service, article_service, vocab_cf
):
    vocabulary_service.create(
        system_identity,
        {"id": "uk", "type": "affiliations", "title": {"en": "Charles University"}},
    )
    vocabulary_service.create(
        system_identity,
        {
            "id": "uk-mff",
            "type": "affiliations",
            "title": {"en": "Faculty of Mathematics and Physics"},
            "hierarchy": {"parent": "uk"},
        },
    )
    Vocabulary.index.refresh()

    article = article_service.create(
        system_identity,
        {"metadata": {"title": "blah", "affiliation": {"id": "uk-mff"}}},
    )

    assert article.data["metadata"]["affiliation"] == {
        "hierarchy": {
            "level": 2,
            "ancestors": ["uk"],
            "ancestors_or_self": ["uk-mff", "uk"],
            "title": [
                {"en": "Faculty of Mathematics and Physics"},
                {"en": "Charles University"},
            ],
            "parent": "uk",
        },
        "id": "uk-mff",
        "title": {"en": "Faculty of Mathematics and Physics"},
        "@v": article.data["metadata"]["affiliation"]["@v"],
    }


@pytest.mark.xfail
def test_facets(
    app,
    db,
    lang_type,
    affiliation_type,
    lang_data,
    vocabulary_service,
    article_service,
    vocab_cf,
):
    with app.test_request_context(headers=[("Accept-Language", "en")]):
        vocabulary_service.create(system_identity, lang_data)
        vocabulary_service.create(
            system_identity,
            {"id": "uk", "type": "affiliations", "title": {"en": "Charles University"}},
        )
        vocabulary_service.create(
            system_identity,
            {
                "id": "uk-mff",
                "type": "affiliations",
                "title": {"en": "Faculty of Mathematics and Physics"},
                "hierarchy": {"parent": "uk"},
            },
        )
        Vocabulary.index.refresh()

        article = article_service.create(
            system_identity,
            {
                "metadata": {
                    "title": "blah",
                    "language": {"id": "eng"},
                    "affiliation": {"id": "uk-mff"},
                }
            },
        )

        ArticleRecord.index.refresh()
        articles = article_service.search(system_identity)
        print(articles.aggregations)
        assert articles.aggregations == {
            "metadata_title": {
                "buckets": [
                    {
                        "key": "blah",
                        "doc_count": 3,
                        "label": "blah",
                        "is_selected": False,
                    }
                ],
                "label": "metadata/title.label",
            },
            "metadata_language": {
                "buckets": [
                    {
                        "key": "eng",
                        "doc_count": 2,
                        "label": "English",
                        "is_selected": False,
                    }
                ],
                "label": "metadata/language.label",
            },
            "metadata_affiliation": {
                "buckets": [
                    {
                        "key": "uk",
                        "doc_count": 2,
                        "label": "Charles University",
                        "is_selected": False,
                    },
                    {
                        "key": "uk-mff",
                        "doc_count": 2,
                        "label": "Faculty of Mathematics and Physics",
                        "is_selected": False,
                    },
                ],
                "label": "metadata/affiliation.label",
            },
        }
