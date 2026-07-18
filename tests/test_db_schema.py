import os

import pytest

psycopg = pytest.importorskip("psycopg")

DATABASE_URL = os.environ.get("DATABASE_URL")
pytestmark = pytest.mark.skipif(not DATABASE_URL, reason="DATABASE_URL not set")

EXPECTED_TABLES = {
    "artifact", "node", "alias", "norm", "op", "ratify_batch", "edge",
    "node_version", "replay_run", "conflict", "notification", "coverage",
    "pending_event", "precedence", "answer_log", "feedback",
}


@pytest.fixture
def conn():
    c = psycopg.connect(DATABASE_URL)
    yield c
    c.rollback()
    c.close()


def test_all_tables_exist(conn):
    rows = conn.execute(
        "SELECT tablename FROM pg_tables WHERE schemaname='public'"
    ).fetchall()
    assert EXPECTED_TABLES <= {r[0] for r in rows}


def test_artifact_append_only(conn):
    conn.execute(
        "INSERT INTO artifact(id, doc_key, doc_type, issuer)"
        " VALUES ('test-sha', 'TEST/DOC', 'thong_tu', 'NHNN')"
    )
    with pytest.raises(psycopg.errors.RaiseException):
        with conn.transaction():
            conn.execute("UPDATE artifact SET title='x' WHERE id='test-sha'")


def test_no_auto_ratify(conn):
    conn.execute(
        "INSERT INTO artifact(id, doc_key, doc_type, issuer)"
        " VALUES ('test-sha3', 'TEST/DOC3', 'thong_tu', 'NHNN')"
    )
    conn.execute(
        "INSERT INTO node(id, artifact_id, path)"
        " VALUES ('00000000-0000-0000-0000-0000000000ba', 'test-sha3', 'dieu:1')"
    )
    with pytest.raises(psycopg.errors.CheckViolation):
        with conn.transaction():
            conn.execute(
                "INSERT INTO op(kind, source_artifact, source_quote, seq, target_node,"
                " new_text, extractor, status)"
                " VALUES ('amend', 'test-sha3', 'q', 1,"
                " '00000000-0000-0000-0000-0000000000ba', 't', 'llm:x', 'ratified')"
            )


def test_ratified_op_immutable(conn):
    conn.execute(
        "INSERT INTO artifact(id, doc_key, doc_type, issuer)"
        " VALUES ('test-sha2', 'TEST/DOC2', 'thong_tu', 'NHNN')"
    )
    conn.execute(
        "INSERT INTO node(id, artifact_id, path)"
        " VALUES ('00000000-0000-0000-0000-0000000000aa', 'test-sha2', 'dieu:1')"
    )
    conn.execute(
        "INSERT INTO op(id, kind, source_artifact, source_quote, seq, target_node,"
        " new_text, extractor, status, ratified_by)"
        " VALUES ('00000000-0000-0000-0000-0000000000ab', 'amend', 'test-sha2', 'q', 1,"
        " '00000000-0000-0000-0000-0000000000aa', 't', 'rule', 'ratified', 'curator:test')"
    )
    with pytest.raises(psycopg.errors.RaiseException):
        with conn.transaction():
            conn.execute(
                "UPDATE op SET new_text='hacked'"
                " WHERE id='00000000-0000-0000-0000-0000000000ab'"
            )
