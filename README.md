# From Git to Gold

This repository contains the starter implementation for the Data Engineering assignment. The instructor notebooks remain unchanged in `reference/`. Service-backed runs require the student's own accounts; no service credentials or fabricated run outputs are included.

## Repository map

- `README.md`: setup, Git command explanations, project map, and validation status.
- `.gitignore`: excludes local `.env`, Python caches, CSV/model outputs, logs, and generated ELT landing data.
- `.env.example`: blank environment-variable template; copy it to `.env` locally and never commit `.env`.
- `requirements.txt`: dependencies for Snowflake, Mage, scikit-learn, RabbitMQ, tests, and report generation.
- `reference/`: original instructor notebooks, preserved unchanged.
- `elt/`: FreshCart ELT notebook and reusable Python/SQL implementation.
- `iris_project/`: Mage project metadata, Iris loader/transformer/exporter blocks, and pipeline graph.
- `stream/`: RabbitMQ dispatcher, driver consumer, and topic-routing helpers.
- `tests/`: pytest checks for the 80/20 split, Mage block functions, FreshCart extraction safeguards, and routing/ACK behavior.
- `.github/workflows/ci.yml`: Python 3.12 GitHub Actions workflow running pytest on pushes and pull requests.
- `reports/assignment_report.md`: evidence-aware report with actual local results and remaining service tasks.
- `reports/build_report.py`: renders the report and screenshot appendix to PDF.
- `reports/RollNo_Name_Pipelines.pdf`: seven-page report draft; replace the filename placeholders and add remaining service evidence/reflection.
- `reports/screenshots/`: captured GitHub Actions run 1 (green) and run 2 (intentional red).

## Local setup

Use Python 3.12, as specified by the assignment. From the repository root in PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest -q
python reports/build_report.py
```

Mage commands:

```powershell
mage run iris_project iris_classifier --test
mage run iris_project iris_classifier --test --runtime-vars '{"max_depth": 3}'
```

For Snowflake, set account/user/password/role values in local `.env`, use a fresh database for B1, and use `SNOWFLAKE_B5_DATABASE` (default `FRESHCART_B5_TEST`) for B5. The code reads credentials from environment variables and does not print them.

For RabbitMQ, set `RABBITMQ_URL` in `.env`, start at least three driver processes in separate terminals, then start the dispatcher:

```powershell
python -m stream.driver Ravi 'bangalore.koramangala.*'
python -m stream.driver Arjun 'bangalore.*.ride'
python -m stream.dispatcher
```

The dispatcher sends one message without `zone` every tenth message. Drivers reject those with `NACK(requeue=False)` and ACK valid requests.

## Git command guide (Part A2)

| Command | Where the change happens | What happens |
| --- | --- | --- |
| `git init` | Local repository metadata | Creates the `.git` database in the working folder. |
| `git add train.py` | Staging area | Selects current file content for the next commit. |
| `git commit -m "msg"` | Local repository | Saves staged content locally; GitHub is not updated. |
| `git remote add origin URL` | Local Git configuration | Records the remote's name and URL. |
| `git push -u origin main` | Remote GitHub repository | Uploads local commits and records the upstream branch. |
| `git pull origin main` | Working folder and local repository | Fetches and integrates remote commits into the current branch. |

A teammate cannot see a local commit on GitHub until it is pushed, and must have repository access.

## Validation status

`python -m pytest -q`: 15 passed. With `test_size=0.3`, the split test failed at 105 training rows; restoring `0.2` passed. Direct local scikit-learn calls measured accuracies 0.633, 0.967, 1.000, 1.000, and 1.000 for depths 1–5, and a depth-3 confusion matrix of 10/9/11 on the diagonal with all four metrics 1.000. These local function results are not Mage CLI executions.

GitHub Actions run 1 passed, run 2 failed on the deliberate `0.3` commit, and run 3 for the corrective `0.2` commit was still running at last check. Screenshots of runs 1 and 2 are saved in `reports/screenshots/` and embedded in the PDF.

Snowflake runs remain pending because no account credentials are configured. Mage CLI/UI runs were not completed locally because the dependency installation was canceled during resolution. Live RabbitMQ delivery remains pending because no broker is configured. The report still requires actual Snowflake/Mage/RabbitMQ evidence, the student's roll number/name, and a personal reflection. The PDF text was supplied in the conversation; its binary `Assignment_DE.pdf` was not present in the workspace.
