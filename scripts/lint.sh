#!/usr/bin/env bash
echo "🔍 Running all linting checks..."
pushd ~/projects/creampie/
pushd cream_api

# Python checks
echo "📝 Running autoflake..."
poetry run autoflake -i -r --remove-all-unused-imports --recursive --remove-unused-variables --in-place --quiet --exclude=__init__.py .

echo "🐍 Running ruff..."
poetry run ruff check --fix .
poetry run ruff format .

echo "🔍 Running mypy..."
poetry run mypy --config-file=pyproject.toml .

popd

# JavaScript/TypeScript checks
pushd cream_ui
echo "📦 Running ESLint..."
yarn eslint --fix .

echo "📘 Running TypeScript type checking..."
yarn tsc --noEmit

echo "💅 Running Prettier..."
yarn prettier

popd
echo "✅ All linting checks completed!"
popd