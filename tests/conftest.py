import os

import pytest
from invenio_app.factory import create_api
from invenio_vocabularies.records.models import VocabularyType


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return create_api


@pytest.fixture(scope="module")
def app_config(app_config):
    """Mimic an instance's configuration."""
    app_config["JSONSCHEMAS_HOST"] = "localhost"
    app_config[
        "RECORDS_REFRESOLVER_CLS"
    ] = "invenio_records.resolver.InvenioRefResolver"
    app_config[
        "RECORDS_REFRESOLVER_STORE"
    ] = "invenio_jsonschemas.proxies.current_refresolver_store"
    app_config["RATELIMIT_AUTHENTICATED_USER"] = "200 per second"
    app_config["SEARCH_HOSTS"] = [
        {
            "host": os.environ.get("OPENSEARCH_HOST", "localhost"),
            "port": os.environ.get("OPENSEARCH_PORT", "9200"),
        }
    ]

    from oarepo_vocabularies.resources.config import VocabulariesResourceConfig
    from oarepo_vocabularies.services.config import VocabulariesConfig

    app_config["VOCABULARIES_SERVICE_CONFIG"] = VocabulariesConfig
    app_config["VOCABULARIES_RESOURCE_CONFIG"] = VocabulariesResourceConfig

    app_config["I18N_LANGUAGES"] = [("en", "English"), ("cs", "Czech")]
    app_config["BABEL_DEFAULT_LOCALE"] = "en"

    # disable redis cache
    app_config["CACHE_TYPE"] = "SimpleCache"  # Flask-Caching related configs
    app_config["CACHE_DEFAULT_TIMEOUT"] = 300
    app_config["SQLALCHEMY_ENGINE_OPTIONS"] = { # hack to avoid pool_timeout set in invenio_app_rdm
        "pool_pre_ping": False,
        "pool_recycle": 3600
    },

    return app_config


@pytest.fixture(scope="module")
def vocabulary_service(app):
    """Vocabularies service object."""
    return app.extensions["invenio-vocabularies"].service


@pytest.fixture()
def lang_type(app, db):
    """Get a language vocabulary type."""
    v = VocabularyType.create(id="languages", pid_type="lng")
    db.session.commit()
    return v


@pytest.fixture()
def affiliation_type(db):
    """Get an affiliation vocabulary type."""
    v = VocabularyType.create(id="institutions", pid_type="institutions")
    db.session.commit()
    return v


@pytest.fixture(scope="function")
def lang_data():
    """Example data."""
    return {
        "id": "eng",
        "title": {"en": "English", "da": "Engelsk"},
        "description": {"en": "English description", "da": "Engelsk beskrivelse"},
        "icon": "file-o",
        "props": {
            "akey": "avalue",
        },
        "tags": ["recommended"],
        "type": "languages",
    }


@pytest.fixture(scope="module")
def article_service(app):
    """Vocabularies service object."""
    return app.extensions["article"].service_records


@pytest.fixture()
def vocab_cf(app, db, cache):
    from oarepo_runtime.services.custom_fields.mappings import prepare_cf_indices

    prepare_cf_indices()
