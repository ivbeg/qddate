# Contributing

Contributions are welcome and greatly appreciated—every bit helps, and credit is always given. You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at <https://github.com/ivbeg/qddate/issues>. When reporting:

- Include your operating system name and version.
- Describe any local setup details that might help with troubleshooting.
- Provide detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for entries tagged with `bug`—they are open to anyone who wants to tackle them.

### Implement Features

Look for issues tagged with `feature`; they are open to anyone. We especially encourage contributions that add support for new languages.

### Write Documentation

qddate always benefits from more documentation—whether in the official docs, docstrings, blog posts, or articles.

### Submit Feedback

The best way to send feedback is to open an issue at <https://github.com/ivbeg/qddate/issues>. When proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible so it remains easy to implement.
- Remember that contributions are always welcome.

## Get Started

Ready to contribute? Here's how to set up `qddate` for local development.

1. Fork the `qddate` repo on GitHub.
2. Clone your fork locally.
3. Install your local copy into a virtual environment. Assuming you use `virtualenvwrapper`, run:

```bash
mkvirtualenv qddate
cd qddate/
python setup.py develop
```

4. Create a branch for local development:

```bash
git checkout -b name-of-your-bugfix-or-feature
```

   Now you can make your changes locally.

5. When you're done, run flake8 and the tests (including the tox matrix):

```bash
pip install -r tests/requirements.txt  # install test dependencies
flake8 qddate tests
nosetests
tox
```

   We use `max-line-length = 100` for flake8 (configured in `setup.cfg`). Install `flake8` and `tox` inside your virtual environment if you do not already have them.

6. Commit your changes and push your branch:

```bash
git add .
git commit -m "Your detailed description of your changes."
git push origin name-of-your-bugfix-or-feature
```

7. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before opening a pull request, ensure that:

1. The PR includes tests.
2. Documentation is updated if the PR adds functionality. Put new functionality inside a function with a docstring and update the feature list in `README.md`.
3. The test suite passes on <https://travis-ci.org/ivbeg/qddate/pull_requests> for all supported Python versions.
4. You follow the core developers' guidance to keep the codebase consistent.
5. If you cannot finish a PR, leave a short comment so someone else can pick it up.

## Guidelines for Adding New Languages

English and Russian are the primary languages in qddate. All languages are pre-configured and manually added for speed optimization. `DateParser` has the `__matchPrefix` method, which filters patterns and minimizes date comparisons.

Languages are added using the `DATE_DATA_TYPES_RAW` constant in `consts.py`. The configuration combines inherited patterns and is manually tuned.

