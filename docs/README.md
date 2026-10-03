# Meridian AI: the learner guide

A friendly, step-by-step guide to the whole project. It assumes you know **Python and LangChain basics** and nothing else. New ideas (FastAPI, logging, Docker, the cloud, …) are explained from the start, with everyday analogies.

> **Is Terraform used?** No. The cloud is set up by **GitHub Actions running `gcloud` commands**. See [14](14-provisioning-and-github-actions.md).

## How to use this guide

1. Read **Start here** in order. It tells the story and gives you the big picture.
2. Open the **repository next to the guide** and follow the file-by-file pages.
3. Run things as you read. Each page ends with something to try.
4. Use **Reference** whenever you get stuck.

## Start here
| # | Page | You will learn |
|---|---|---|
| 01 | [The case](01-the-case.md) | The problem the app solves, who uses it, and four scenarios to try |
| 02 | [The big picture](02-the-big-picture.md) | How everything fits, using a restaurant picture |
| 03 | [Basics for newcomers](03-basics-for-newcomers.md) | What a repo, package, `.env`, API, container is |
| 15 | [What you need](15-requirements-accounts-costs.md) | Skills, accounts, software, the **$300 free credit**, costs |

## Understand the code
| # | Page | You will learn |
|---|---|---|
| 04 | [Project tour](04-project-tour.md) | Every folder, and **why the code is split into many files** |
| 05 | [Backend, file by file](05-backend-files.md) | Every Python file: job, contents, connections |
| 06 | [Frontend, file by file](06-frontend-files.md) | The screens and how they call the backend |
| 07 | [Root and config files](07-root-and-config-files.md) | Dockerfile, requirements, `.env.example`, the workflow… |
| 08 | [Follow a request](08-follow-a-request.md) | Upload, ask and audit traced through the files |

## Understand the ideas
| # | Page | You will learn |
|---|---|---|
| 09 | [FastAPI explained](09-fastapi-explained.md) | HTTP, checking data, `def` vs `async def`, CORS |
| 10 | [Settings and logging](10-settings-and-logging.md) | `.env`, log levels, structured logs, where to read them |
| 11 | [Document Q&A (RAG)](11-rag-explained.md) | Chunks, embeddings, vector search |
| 12 | [Agents](12-agents-explained.md) | Tools, prompts, the supervisor |

## Run and ship
| # | Page | You will learn |
|---|---|---|
| – | [Run it locally](../README.md#run-it-on-your-computer) | Quick start, in the main README |
| 13 | [Docker and Cloud Run](13-docker-and-cloud-run.md) | Packing and running on the internet |
| 14 | [Provisioning and GitHub Actions](14-provisioning-and-github-actions.md) | How the cloud things get created |
| – | [Deploy to Google Cloud](../DEPLOY.md) | Step by step, plus clean-up |

## Practise and reference
| # | Page | What it is |
|---|---|---|
| 16 | [Exercises](16-exercises.md) | Hands-on tasks with hints |
| 17 | [Why it is built this way](17-why-built-this-way.md) | The reason behind each choice |
| 18 | [Troubleshooting](18-troubleshooting.md) | Symptoms, causes, fixes |
| 19 | [Glossary](19-glossary.md) | Plain-English definitions |
| – | [examples/](examples/README.md) | Six small programs to run (no accounts needed) |

> **Aldermoor Industries is fictional.** The sample documents are made up.
