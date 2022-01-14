## How to contribute to Specify Systems Lifemapper lmpy

#### You found a bug

* Check that it hasn't already be reported by searching our GitHub issues
[Issues](https://github.com/specifysystems/lmpy/issues).

* If you're unable to find an open issue addressing the problem,
* [open a new one](https://github.com/specifysystems/lmpy/issues/new?assignees=cjgrady&template=bug_report.md).
* Be sure to include a **title and clear description**, as much relevant information as possible, and a
  **code sample** or an **executable test case** demonstrating the expected behavior that is not occurring.


#### You wrote a patch for a bug

* Open a new GitHub pull request with the patch.

* Ensure the pull request description clearly describes the problem and solution. Include the relevant issue number if applicable.

* Before submitting, check that your patch follows our coding and testing conventions


#### You want to add a new analysis

* [Submit a new GitHub issue](https://github.com/specifysystems/lmpy/issues/new?assignees=&template=feature_request.md) and suggest
  your analysis.  We want to make sure that it fits before you spend time coding it.

* Write your code and tests following our coding and testing conventions.

* Submit a pull request


#### Coding conventions

* We utilize [pre-commit](https://pre-commit.com/) to ensure that we have consistent coding style and practices throughout the project.

* Our pre-commit hooks use [black](https://pypi.org/project/black/), [flake8](https://flake8.pycqa.org/en/latest/) and others.  You
  can see all of the enabled pre-commit hooks at [.pre-commit.yml](.pre-commit.yml) and any exceptions for various linters at
  [linter configuration](.github/linters/).

* Doc strings should follow [Google Style Guidelines](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)

* Check code style against our requirements by running all pre-commit hoooks.

```
$ pre-commit run -a
```

* We use [pytest](https://docs.pytest.org/en/latest/) style tests

* Use pytest with coverage to determine if test code is adequate.  There is a GitHub action in place that will require tests to pass
  before code can be merged.

```
$ pytest tests/ -v --cov lmpy --cov-report term-missing
```

#### You want to update documentation

* Update the documentation in a new branch

* Open and submit a new pull request for your updates

* Documentation is built via GitHub actions and deployed as GitHub pages and a pdf manual.


Thanks!

Lifemapper Team
