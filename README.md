# From Git to Gold

This repository is the starter structure for the data engineering assignment, based on the supplied assignment PDF and instructor notebooks. The original notebooks are retained under `reference/` and are not modified. Parts B, C, and D remain unimplemented.

## Project contents


## Dependencies

The requirements are based on imports and installation commands in the provided notebooks and assignment: `snowflake-connector-python` and `pandas` for FreshCart; `mage-ai`, `scikit-learn`, and `joblib` for the Iris example; `pika` for the RabbitMQ scripts; and `pytest` for tests. The `uv` utility in the Mage notebook is only used there to create its example environment and is not included as a project runtime dependency.

## Credentials

Do not commit passwords, tokens, or other credentials. Keep local values in `.env` or environment variables; `.env` files are ignored by Git. The supplied FreshCart notebook is preserved as-is and requests a password interactively, but it also contains account/user configuration. Review instructor-provided configuration before publishing the reference material. Keep any hosted RabbitMQ URL out of Git.

## Assignment status

This scaffold establishes folders and project configuration only. The `prepare_data` test follows the PDF's 120-train/30-test requirement but remains skipped until that Part C block exists. No Part B, C, or D implementation has been added. The assignment also calls for at least five meaningful commits over its course; those should be made as work progresses rather than as one final commit.

This repository contains the starter implementation for the Data Engineering assignment. The instructor notebooks remain unchanged in `reference/`. Service-backed runs require the student's own accounts; this repository does not contain service credentials or fabricated run outputs.

## Repository map

- `README.md`: setup, Git command explanations, folder map, and validation status.
- `.gitignore`: excludes local `.env`, Python caches, CSV/model outputs, logs, and generated ELT landing data.
- `.env.example`: blank environment-variable template; copy it to `.env` locally and never commit `.env`.
- `requirements.txt`: runtime and test dependencies for Snowflake, Mage, scikit-learn, RabbitMQ, and pytest.
- `reference/`: the two original instructor notebooks, preserved as read-only source material.
- `elt/`: `freshcart_elt.ipynb` demonstrates the Snowflake workflow; `freshcart_pipeline.py` holds reusable ELT functions and SQL.
- `iris_project/`: Mage project metadata, Iris loader/transformer/exporter blocks, tests, and pipeline graph.
- `stream/`: RabbitMQ dispatcher, driver consumer, and pure topic-routing helpers.
- `tests/`: local pytest checks for the split, Mage block functions, FreshCart safeguards, and routing/ACK decisions.
- `.github/workflows/ci.yml`: GitHub Actions workflow for Python 3.12, dependency installation, and pytest on every push and pull request.
- `reports/assignment_report.md`: evidence-aware report draft, including source-derived calculations and clearly marked external-run gaps.
- `reports/build_report.py`: renders the report draft as a compact PDF.
- `reports/RollNo_Name_Pipelines.pdf`: generated report draft using the assignment's filename template; replace the placeholders after adding identifying details and evidence.

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

The Mage pipeline can be run with:

```powershell
mage run iris_project iris_classifier --test
mage run iris_project iris_classifier --test --runtime-vars '{"max_depth": 3}'
```

Open `elt/freshcart_elt.ipynb` and execute it top to bottom after setting Snowflake account/user/password/role variables in `.env`. Use a new database for B1; the B5 failure exercise uses a separate `SNOWFLAKE_B5_DATABASE` (default `FRESHCART_B5_TEST`). The notebook and `elt/freshcart_pipeline.py` read credentials from the environment; no credential values should be copied into source.

Set `RABBITMQ_URL` in local `.env` before running:

```powershell
python -m stream.driver Ravi 'bangalore.koramangala.*'
python -m stream.driver Arjun 'bangalore.*.ride'
python -m stream.dispatcher
```

Run at least three driver processes in separate terminals. The dispatcher sends one message without a `zone` every tenth message. Drivers reject those messages with `NACK(requeue=False)` and acknowledge valid messages.

## Git command guide (Part A2)

| Command | Where the change happens | What happens |
| --- | --- | --- |
| `git init` | Local repository metadata | Creates the `.git` database in the working folder. |
| `git add train.py` | Staging area | Selects the current `train.py` content for the next commit. |
| `git commit -m "msg"` | Local repository | Saves staged content as a local snapshot; it does not publish it to GitHub. |
| `git remote add origin URL` | Local repository configuration | Records a name and URL for a remote repository. |
| `git push -u origin main` | Remote GitHub repository | Uploads local commits on `main` and records the upstream branch. |
| `git pull origin main` | Working folder and local repository | Fetches remote commits and integrates them into the current branch. |

A teammate cannot see a new local commit on GitHub until it has been pushed to the remote (assuming they have access to the repository).

## Assignment status

Implemented locally: the Part A CI workflow and exact 120/30 test; Mage-compatible Iris blocks including the 80/20 split, accuracy gate, evaluation branch, exporter and tested validation block; FreshCart SQL/data flow and credential-based notebook; RabbitMQ scripts and topic-routing/ACK-NACK unit tests; blank `.env.example`.

Locally verified: `python -m pytest -q` passed 15 tests. The required temporary `test_size=0.3` produced a failing 80/20 test (105 train rows); restoring `0.2` passed. Direct scikit-learn function execution measured accuracies of 0.633, 0.967, 1.000, 1.000, and 1.000 for depths 1 through 5, respectively. At default depth 3, direct evaluation produced a 10/9/11 diagonal confusion matrix and 1.000 for accuracy, precision, recall, and F1. These are local Python function results, not Mage CLI runs or GitHub Actions evidence.

Not yet verified: Snowflake baseline/change-history/idempotency and failure outputs (no credentials configured); Mage CLI/UI runs (the full dependency installation was canceled during Mage dependency resolution); live RabbitMQ delivery (no local broker is listening and no broker URL is configured); and green/red GitHub Actions screenshots (no commits have been pushed). The PDF is a draft and still needs actual service evidence, the student's identifying details, and a personal reflection. The assignment requires at least five meaningful commits over its course; continue committing each completed milestone rather than squashing everything at the end.

The uploaded PDF text is the assignment specification. The binary `Assignment_DE.pdf` was not present in the workspace when this README was updated.
