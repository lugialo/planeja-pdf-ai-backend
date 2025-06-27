-- Script para criar os bancos de dados necessários
CREATE DATABASE planeja_main;
CREATE DATABASE planeja_platform;

-- Conectar ao banco planeja_platform e criar algumas tabelas de exemplo para teste
\c planeja_platform;

-- Enum para status do orçamento
CREATE TYPE budget_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED', 'DRAFT');

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de orçamentos
CREATE TABLE IF NOT EXISTS budgets (
    id TEXT PRIMARY KEY,
    "userId" TEXT REFERENCES users(id),
    name TEXT NOT NULL,
    status budget_status DEFAULT 'PENDING',
    total DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inserir dados de exemplo
INSERT INTO users (id, name, email) VALUES 
('test_user_123', 'Usuario Teste', 'teste@email.com'),
('user_456', 'Outro Usuario', 'outro@email.com')
ON CONFLICT (id) DO NOTHING;

INSERT INTO budgets (id, "userId", name, status, total) VALUES 
('budget_1', 'test_user_123', 'Orçamento Janeiro', 'APPROVED', 1500.00),
('budget_2', 'test_user_123', 'Orçamento Fevereiro', 'PENDING', 2000.00),
('budget_3', 'test_user_123', 'Orçamento Março', 'APPROVED', 1800.00),
('budget_4', 'test_user_123', 'Orçamento Abril', 'REJECTED', 1200.00),
('budget_5', 'user_456', 'Orçamento Outro', 'APPROVED', 3000.00)
ON CONFLICT (id) DO NOTHING;
