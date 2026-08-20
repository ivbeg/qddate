@ECHO OFF
REM Build or serve the Docusaurus documentation site (requires Node.js 18+).

if "%1"=="docs" goto docs
if "%1"=="docs-serve" goto docs_serve
if "%1"=="docs-patterns" goto docs_patterns

echo Available targets: docs, docs-serve, docs-patterns
echo Use Makefile on Unix: make docs
goto end

:docs
cd docs
call npm ci
call npm run build
cd ..
goto end

:docs_serve
cd docs
call npm start
cd ..
goto end

:docs_patterns
python scripts/generate_pattern_docs.py
goto end

:end
