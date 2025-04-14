-- Match vectors using cosine distance represented by the symbole <=>.
-- The cosine distance range between 0 (perfect match) and 2 (opposite)
-- The cosine distance = 1 - Cosine similarity (range -1 to 1)
create or replace function match_documents (
  query_embedding vector(1536),
  match_threshold float,
  match_count int
)
returns table (
  id bigint,
  title text,
  body text,
  similarity float
)
language sql stable
as $$
  select
    documents.id,
    documents.title,
    documents.body,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where 1 - (documents.embedding <=> query_embedding) > match_threshold
  order by (documents.embedding <=> query_embedding) asc
  limit match_count;
$$;


-- Enable the "vector" extension.
create extension vector
with schema extensions;

-- Disable the "vector" extension
-- drop extension if exists vector;

-- Create "documents" table
create table documents (
  id serial primary key,
  title text not null,
  body text not null,
  source text,
  embedding vector(1536)
);