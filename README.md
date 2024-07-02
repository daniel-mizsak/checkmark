## <div align="center"> ✅ checkmark</div>

<div align="center">
<a href="https://github.com/daniel-mizsak/checkmark/actions/workflows/ci.yml" target="_blank"><img src="https://github.com/daniel-mizsak/checkmark/actions/workflows/ci.yml/badge.svg" alt="build status"></a>
<a href="https://results.pre-commit.ci/latest/github/daniel-mizsak/checkmark/main" target="_blank"><img src="https://results.pre-commit.ci/badge/github/daniel-mizsak/checkmark/main.svg" alt="pre-commit.ci status"></a>
<a href="ttps://img.shields.io/github/license/daniel-mizsak/checkmark" target="_blank"><img src="https://img.shields.io/github/license/daniel-mizsak/checkmark" alt="license"></a>
</div>


## Overview
Checkmark is an automated assessment generator and evaluator system.

It works with a predefined question pool and a list of students, and generates quizzes in a format that later can be automatically evaluated by taking a picture of the submission.<br>


## Getting started
<details>
<summary>Motivation</summary>
<br>

Tools that enable automatic quiz evaluation have been around for years.
One example for this is the <a href="https://mateprod.blob.core.windows.net/media/Default/images/Kodlap_Minta.pdf">International Kangaroo Mathematics Contest</a>, which is a multiple-choice test, and the evaluation is done by a computer.

However, these tools require a very specific layout for the submission of the solution.

Unfortunately **Checkmark** is not able solve the general problem and evaluate any kind of submission, but it tries to solve the problem by enabling teachers to generate assessments from their own question pool in an expected layout format.
This makes it possible to evaluate these assessments automatically by scanning the submissions with a mobile phone and thus saving a lot of time for the teachers.
<br>
</details>

<details>
<summary>Installation</summary>
<br>

Currently the application is only runnable from the source code. However, it is planned to create a standalone executable file in the future.

To run the application you need `python` installed on your computer.

- Create and activate a new virtual environment in the root folder of the project:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

- Install the code as a packages:
    ```bash
    pip install .
    ```

- Verify that the installation was successful:
    ```
    checkmark --version
    ```

- Run the GUI and generate some assessments:
    ```
    checkmark generate
    ```
</details>

<details>
<summary>Using Checkmark</summary>
<br>

To use the application the following files are needed:

- Questions in an *Excel* file (with the expected format) located in the following folder:
`data/assessments/<SUBJECT NAME>-<CLASS NUMBER>/<TOPIC NAME>.xlsx`

- List of students of each class in a *csv* file located as such:
`data/classes/<CLASS NUMBER>-<CLASS TYPE>.csv`

</details>
