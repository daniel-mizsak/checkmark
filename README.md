## <div align="center"> ✅ Checkmark</div>
<br>

[![build status](https://github.com/daniel-mizsak/checkmark/actions/workflows/main.yaml/badge.svg)](https://github.com/daniel-mizsak/checkmark/actions/workflows/main.yaml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/daniel-mizsak/checkmark/main.svg)](https://results.pre-commit.ci/latest/github/daniel-mizsak/checkmark/main)
[![license](https://img.shields.io/github/license/daniel-mizsak/check-mark)](https://img.shields.io/github/license/daniel-mizsak/check-mark)


Checkmark is an automated assessment creation and evaluation system.

It works with a predefined question pool and a list of students, and generates quizzes in a format that later can be automatically evaluated by taking a picture of the submission.

<br>

## <div align="center"> Description </div>
<details>
<summary>Motivation</summary>
Tools that enable us to automatically evaluate quizzes have been around for years.
One example for this is the <a href="https://mateprod.blob.core.windows.net/media/Default/images/Kodlap_Minta.pdf">International Kangaroo Mathematics Contest</a>, which is a multiple-choice test, and the evaluation is done by a computer.

However, these tools require a very specific layout for the submission of the solution.

Unfortunately **Checkmark** is not able solve the general problem and evaluate any kind of submission, but it tries to solve the problem by enabling teachers to generate assessments from their own question pool in an expected layout format.
This makes it possible to evaluate these assessments automatically by scanning the submissions with a mobile phone and thus saving a lot of time for the teachers.
</details>

<br>

<details>
<summary>Installation</summary>
Currenly the application is only runnable from the source code. However, it is planned to create a standalone executable file in the future.

To run the application you need `python` installed on your computer.

- Create and activate a new virtual environment in the root folder of the project ([how to use venv](https://docs.python.org/3/library/venv.html))

- Install the necessary packages:
    `pip install -r requirements.txt`

- Run the GUI and generate some assessments:
    `python run.py`
</details>

<br>

<details>
<summary>How to use</summary>
To use the application the following files are needed:

- Questions in an *Excel* file (with the expected format) located in the following folder:
`data/assessments/<SUBJECT NAME>-<CLASS NUMBER>/<TOPIC NAME>.xlsx`

- List of students of each class in a *csv* file located as such:
`data/classes/<CLASS NUMBER>-<CLASS TYPE>.csv`
</details>

## <div align="center"> Future plans</div>
The following features are planned to be implemented in the future:
- New question types such as *True/False*, *Ordering*, *Fill in the blanks*
- Unassigned assessments for students being late from class
- Group assignments instead of individual ones
- Inserting images between questions
- Low effort question sharing between teachers
- Standalone executable file
- Detailed documentation about the results of the class


## <div align="center"> Contribute</div>

[Mizsák Dániel](https://www.linkedin.com/in/daniel-mizsak)

[Pecsenye Samu](https://www.linkedin.com/in/samu-pecsenye/)
