# Database Management Style Guide (PostgreSQL Focus)

> This guide provides best practices and standards for managing PostgreSQL databases in the CreamPie project. It covers schema design, naming conventions, migrations, performance, security, and operational procedures.

## Table of Contents
1. [General Principles](#general-principles)
2. [Schema and Table Design](#schema-and-table-design)
3. [Naming Conventions](#naming-conventions)
4. [Data Types and Constraints](#data-types-and-constraints)
5. [Indexing and Performance](#indexing-and-performance)
6. [Migrations and Versioning](#migrations-and-versioning)
7. [Security and Access Control](#security-and-access-control)
8. [Backup and Recovery](#backup-and-recovery)
9. [Testing and Local Development](#testing-and-local-development)
10. [Example Patterns](#example-patterns)

---

## General Principles
- Use PostgreSQL as the primary RDBMS for all persistent data.
- Prefer declarative schema management (SQLAlchemy ORM, Alembic migrations, or raw SQL scripts tracked in VCS).
- All schema changes must be version-controlled and peer-reviewed.
- Design for data integrity, scalability, and maintainability.
- Document all non-obvious schema decisions and business rules.

## Schema and Table Design
- Group related tables into schemas if the project grows large (e.g., `public`, `analytics`, `auth`).
- Prefer narrow tables (fewer columns) and normalized design for transactional data.
- **Always prefer a UUIDv4 (`uuid_generate_v4()` or `gen_random_uuid()`) over an integer ID for primary keys.**
- Use surrogate primary keys (e.g., `SERIAL`, `BIGSERIAL`, or `UUID`) unless a natural key is clearly superior.
- Always define primary keys for every table.
- Use foreign keys to enforce referential integrity.
- Use `NOT NULL` constraints wherever possible.
- Avoid storing redundant or denormalized data unless justified for performance.
- Use check constraints for domain validation (e.g., `CHECK (status IN ('active', 'inactive'))`).

## Naming Conventions
- Use **lowercase with underscores** for all identifiers (tables, columns, indexes, constraints).
- Table names: plural nouns (e.g., `users`, `orders`, `stock_data`).
- Column names: singular, descriptive (e.g., `user_id`, `created_at`, `status`).
- Primary key: `id` or `<table>_id` (e.g., `user_id` in `users` table).
- Foreign key: `<referenced_table>_id` (e.g., `user_id` in `orders`).
- Indexes: `idx_<table>_<column1>_<column2>`
- Unique constraints: `uq_<table>_<column1>_<column2>`
- Check constraints: `ck_<table>_<description>`
- Foreign key constraints: `fk_<fromtable>_<totable>`
- Sequences: `seq_<table>_<column>`

## Data Types and Constraints
- Use the most specific data type possible (e.g., `INTEGER` for counts, `BOOLEAN` for flags, `TIMESTAMP WITH TIME ZONE` for times).
- Use `UUID` for distributed or public-facing identifiers.
- Use `TEXT` for variable-length strings, `VARCHAR(n)` only if you must enforce a length.
- Use `NUMERIC` for monetary values (never `FLOAT` or `REAL`).
- Use `BOOLEAN` for true/false fields.
- Use `ARRAY`, `JSONB`, or `ENUM` types only when justified.
- Always specify `DEFAULT` values for columns where appropriate.
- Use `CHECK` constraints for value validation.

## Indexing and Performance
- Always index primary and foreign keys.
- Add indexes for columns frequently used in `WHERE`, `ORDER BY`, or `JOIN` clauses.
- Use multi-column indexes for common query patterns.
- Avoid over-indexing; each index adds write overhead.
- Use `EXPLAIN` to analyze query plans and optimize as needed.
- Consider partial indexes for sparse data.
- Use `UNIQUE` indexes to enforce business rules.

## Migrations and Versioning
- Use Alembic (or similar) for schema migrations; never edit the database schema manually in production.
- Each migration should be atomic and reversible.
- Name migration scripts descriptively (e.g., `20250127_add_user_status_column.py`).
- Test migrations on a staging or local environment before applying to production.
- Keep migration history in version control.

## Security and Access Control
- Use least-privilege principle for database users/roles.
- Never use superuser or admin accounts for application connections.
- Store credentials securely (e.g., environment variables, secrets manager).
- Use SSL/TLS for all database connections.
- Restrict network access to the database (firewall, VPC, etc.).
- Regularly audit user privileges and revoke unused accounts.
- Use row-level security (RLS) if needed for multi-tenant data.

## Backup and Recovery
- Schedule regular automated backups (e.g., `pg_dump`, managed service snapshots).
- Test restore procedures regularly.
- Store backups securely and offsite if possible.
- Document backup and recovery procedures.
- Monitor backup job success/failure.

## Testing and Local Development
- Use a separate database for development and testing.
- Use fixtures or factories to seed test data.
- Run migrations as part of test setup.
- Use transaction rollbacks to isolate tests.
- Use in-memory or temporary databases for fast unit tests when possible.
- Never run destructive tests against production data.

## Example Patterns

### Table Definition Example
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    status TEXT NOT NULL DEFAULT 'active',
    CHECK (status IN ('active', 'inactive', 'banned'))
);
```

### Index Example
```sql
CREATE INDEX idx_users_email ON users(email);
```

### Foreign Key Example
```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Alembic Migration Example
```python
# 20250127_add_user_status_column.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('users', sa.Column('status', sa.Text(), nullable=False, server_default='active'))

def downgrade():
    op.drop_column('users', 'status')
```

---

This style guide provides a foundation for robust, secure, and maintainable PostgreSQL database management. Follow these patterns to ensure data integrity, performance, and operational excellence.
