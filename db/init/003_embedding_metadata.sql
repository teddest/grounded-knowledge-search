ALTER TABLE sections
    ADD COLUMN IF NOT EXISTS embedding_model TEXT;

ALTER TABLE sections
    ADD COLUMN IF NOT EXISTS embedding_input_hash TEXT;

CREATE INDEX IF NOT EXISTS sections_embedding_model_idx
    ON sections (document_id, embedding_model);
