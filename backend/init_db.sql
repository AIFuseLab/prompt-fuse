-- Switch to default database first
\c postgres;

-- Drop and create the database
DROP DATABASE IF EXISTS prompt_fuse;
CREATE DATABASE prompt_fuse;

-- Connect to the new database
\c prompt_fuse;

-- Create the projects table
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS llm;
DROP TABLE IF EXISTS prompt_template;
DROP TABLE IF EXISTS prompts;
DROP TABLE IF EXISTS tests;
DROP TABLE IF EXISTS test_prompt_association;

-- Create the projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Create the llm table
CREATE TABLE llm (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    access_key VARCHAR(255),
    secret_access_key VARCHAR(255),
    aws_region VARCHAR(100),
    llm_model_id VARCHAR(255)
);

-- Create the prompt_template table
CREATE TABLE prompt_template (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    number_of_prompts INTEGER DEFAULT 0,
    project_id UUID,
    CONSTRAINT fk_project
        FOREIGN KEY (project_id)
        REFERENCES projects(id)
);

-- Create the prompts table
CREATE TABLE prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    prompt TEXT,
    notes TEXT,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version NUMERIC(3, 1) DEFAULT 0.0,
    llm_id UUID,
    prompt_template_id UUID,
    CONSTRAINT fk_llm
        FOREIGN KEY (llm_id) 
        REFERENCES llm(id),
    CONSTRAINT fk_project
        FOREIGN KEY (prompt_template_id) 
        REFERENCES prompt_template(id)
);

-- Create the tests table
CREATE TABLE tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_name VARCHAR(255) NOT NULL,
    user_input TEXT,
    creation_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    image BYTEA
);

-- Create the test_prompt_association table
CREATE TABLE test_prompt_association (
    test_id UUID REFERENCES tests(id) ON DELETE CASCADE,
    prompt_id UUID REFERENCES prompts(id) ON DELETE CASCADE,
    PRIMARY KEY (test_id, prompt_id),
    llm_response TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    latency_ms NUMERIC,
    prompt_tokens INTEGER,
    user_input_tokens INTEGER
);