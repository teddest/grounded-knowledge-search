CREATE TABLE IF NOT EXISTS document_sets (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    root_path TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'registered'
        CHECK (status IN ('registered', 'indexing', 'ready', 'error')),
    last_indexed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY,
    document_set_id UUID NOT NULL REFERENCES document_sets(id) ON DELETE CASCADE,
    source_path TEXT NOT NULL,
    title TEXT NOT NULL,
    category TEXT,
    status TEXT,
    version TEXT,
    effective_date DATE,
    audience TEXT,
    owner TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    content_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (document_set_id, source_path)
);

CREATE TABLE IF NOT EXISTS sections (
    id BIGSERIAL PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    ordinal INTEGER NOT NULL,
    heading_path TEXT[] NOT NULL DEFAULT '{}',
    start_line INTEGER,
    end_line INTEGER,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    embedding_model TEXT,
    embedding_input_hash TEXT,
    search_vector TSVECTOR NOT NULL DEFAULT ''::tsvector,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (document_id, ordinal)
);

CREATE TABLE IF NOT EXISTS index_runs (
    id UUID PRIMARY KEY,
    document_set_id UUID NOT NULL REFERENCES document_sets(id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'failed')),
    documents_seen INTEGER NOT NULL DEFAULT 0,
    sections_seen INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS documents_document_set_idx
    ON documents (document_set_id);

CREATE INDEX IF NOT EXISTS documents_status_idx
    ON documents (document_set_id, status);

CREATE INDEX IF NOT EXISTS sections_document_idx
    ON sections (document_id, ordinal);

CREATE INDEX IF NOT EXISTS sections_search_vector_idx
    ON sections USING GIN (search_vector);

CREATE INDEX IF NOT EXISTS sections_embedding_idx
    ON sections USING hnsw (embedding vector_cosine_ops)
    WHERE embedding IS NOT NULL;
