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
