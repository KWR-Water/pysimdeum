# Contributing to `pysimdeum`
We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

Following these guidelines helps to communicate that you respect the time of the developers managing and developing this 
open source project. In return, they should reciprocate that respect in addressing your issue, assessing changes, and 
helping you finalize your pull requests.

## Our Development Process
We use [Github Actions](https://docs.github.com/en/actions), so all code changes happen through pull requests (PRs).
Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Report bugs
We use Github's [issues](https://github.com/KWR-Water/pysimdeum/issues) to track public bugs. Report a bug by [opening a new 
issue](https://github.com/KWR-Water/pysimdeum/issues/new/choose); it's that easy!

For us to be able to fix a bug, we require information about the bug. **Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

People *love* thorough bug reports. I'm not even kidding.

## Request a feature
If you want a new feature in `pysimdeum`, please provide us with a use case and a description of what is missing. If 
possible, provide a code snippet that describes your use case. If you already have a solution for the implementation,
please add this to the issue as well.

## Security issues
If you find a security vulnerability, do NOT open an issue. Email pysimdeum@gmail.com instead.

## Style and standards
`pysimdeum` uses a few standards to simplify its development. Please adhere to them.

### Coding Style
Codes will be linted by [black](https://github.com/psf/black) as part of the CI pipeline. This means, that in general 
you don't have to concern yourself with linting.

### Github issue labels
[StandardIssueLabels](https://github.com/wagenet/StandardIssueLabels#standardissuelabels) are used for labeling issues. 
Please read the description to choose the correct label(s) for your issue.

### Git commit messages
Semantic Versioning is used to calculate the next version number based of the commits and their corresponding commit 
message. We use the [Angular Commit message format](https://github.com/angular/material/blob/master/.github/CONTRIBUTING.md#submit) 
for this purpose. Please, adhere to this standard, if you want your PR to be merged.

Versions look like this: MAJOR.MINOR.PATCH

For now, MAJOR is set to 0 until `pysimdeum` is deemed stable.

## Code of Conduct
Please read our [Code of Conduct](https://github.com/KWR-Water/pysimdeum/blob/master/CODE_OF_CONDUCT.md) before interacting with
the `pysimdeum` team or the community. Violations will be met with clear consequences.

## License
In short, when you submit code changes, your submissions are understood to be under the same 
[EUPLv1.2 License](https://joinup.ec.europa.eu/sites/default/files/custom-page/attachment/2020-03/EUPL-1.2%20EN.txt) that covers the project.

## References
This document was adapted from the open-source contribution guidelines by 
[Brian Danielak](https://gist.github.com/briandk/3d2e8b3ec8daf5a27a62) which is based on the guidelines for 
[Meta's Draft-JS](https://github.com/facebook/draft-js/blob/master/CONTRIBUTING.md)