import json
import time

from article.records.api import ArticleRecord
from invenio_access.permissions import system_identity
from invenio_vocabularies.records.api import Vocabulary


def test_language_reference(
    app,
    db,
    lang_type,
    lang_data,
    vocabulary_service,
    article_service,
    vocab_cf,
    search_clear,
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
    app,
    db,
    affiliation_type,
    lang_type,
    vocabulary_service,
    article_service,
    vocab_cf,
    client,
    search_clear,
):
    vocabulary_service.create(
        system_identity,
        {"id": "uk", "type": "institutions", "title": {"en": "Charles University"}},
    )
    vocabulary_service.create(
        system_identity,
        {"id": "en", "type": "languages", "title": {"en": "English"}},
    )
    vocabulary_service.create(
        system_identity,
        {
            "id": "uk-mff",
            "type": "institutions",
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
                "language": {"id": "en"},
                "affiliation": {"id": "uk-mff"},
            }
        },
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
            "leaf": True,
            "parent": "uk",
        },
        "id": "uk-mff",
        "title": {"en": "Faculty of Mathematics and Physics"},
        "@v": article.data["metadata"]["affiliation"]["@v"],
    }

    ArticleRecord.index.refresh()

    # t1 = time.time()
    # for i in range(100):
    #     article_from_service = article_service.read(system_identity, article.id)
    # t2 = time.time()
    # print(f"Single read via service takes {(t2-t1)/100 * 1000} msecs")
    #
    # t1 = time.time()
    # for i in range(100):
    #     article_from_client = client.get(f'/article/{article.id}')
    #     article_from_service_data = article_from_client.json
    #     assert article_from_client.status_code == 200
    # t2 = time.time()
    # print(f"Single read via client takes {(t2-t1)/100 * 1000} msecs")
    #
    # t1 = time.time()
    # for i in range(100):
    #     article_from_client = client.get(f'/article/{article.id}', headers={'Accept': "application/vnd.inveniordm.v1+json"})
    #     article_from_service_data = article_from_client.json
    #     assert article_from_client.status_code == 200
    # t2 = time.time()
    # print(f"Single UI read via client takes {(t2-t1)/100 * 1000} msecs")

    # t1 = time.time()
    # for i in range(100):
    #     article_from_client = client.get(f'/article/')
    #     article_from_client_data = article_from_client.json
    #     assert article_from_client.status_code == 200
    # t2 = time.time()
    # print(f"Single listing takes {(t2-t1)/100 * 1000} msecs")

    t1 = time.time()
    for i in range(100):
        article_from_client = client.get(
            f"/article/", headers={"Accept": "application/vnd.inveniordm.v1+json"}
        )
        article_from_service_data = json.loads(article_from_client.data.decode("utf-8"))
        assert article_from_client.status_code == 200
    t2 = time.time()
    print(f"Single UI listing takes {(t2-t1)/100 * 1000} msecs")


def test_facets(
    app,
    db,
    lang_type,
    affiliation_type,
    lang_data,
    vocabulary_service,
    article_service,
    vocab_cf,
    search_clear,
):
    with app.test_request_context(headers=[("Accept-Language", "en")]):
        vocabulary_service.create(system_identity, lang_data)
        vocabulary_service.create(
            system_identity,
            {"id": "uk", "type": "institutions", "title": {"en": "Charles University"}},
        )
        vocabulary_service.create(
            system_identity,
            {
                "id": "uk-mff",
                "type": "institutions",
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
        assert json.loads(json.dumps(articles.aggregations, default=str)) == {
            "metadata_title": {
                "buckets": [
                    {
                        "key": "blah",
                        "doc_count": 1,
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
                        "doc_count": 1,
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
                        "doc_count": 1,
                        "label": "Charles University",
                        "is_selected": False,
                    },
                    {
                        "key": "uk-mff",
                        "doc_count": 1,
                        "label": "Faculty of Mathematics and Physics",
                        "is_selected": False,
                    },
                ],
                "label": "metadata/affiliation.label",
            },
            "metadata_props": {"buckets": [], "label": "metadata/props.label"},
        }


def test_props(
    app,
    db,
    lang_type,
    lang_data,
    vocabulary_service,
    article_service,
    vocab_cf,
    search_clear,
):
    vocabulary_service.create(system_identity, lang_data)
    Vocabulary.index.refresh()

    article = article_service.create(
        system_identity, {"metadata": {"title": "blah", "props": {"id": "eng"}}}
    )

    assert article.data["metadata"]["props"]["akey"] == "avalue"
