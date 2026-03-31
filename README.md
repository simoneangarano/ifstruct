# IFStruct

Standalone, frozen implementation of the `ifstruct` eval.

This repo contains:

- a precomputed 2,000-example test set in `data/test.jsonl`
- a small OpenAI-compatible eval runner using `requests`
- the validator used to score JSON/YAML structured-output responses

## Install

```bash
cd ~/code/evals/ifstruct
uv sync
```

## Configure

Create a local env file from the example:

```bash
cp .env.example .env
```

Set these values in `.env`:

```bash
BASE_URL=https://openrouter.ai/api/v1
API_KEY=your-api-key-here
```

The CLI automatically loads `.env` if it exists, and it also works if `BASE_URL` and `API_KEY` are already exported in your shell.

## Run

```bash
uv run ifstruct-eval \
  --model google/gemini-3-flash-preview \
  --dataset data/test.jsonl \
  --results-file results/latest.json \
  --n-threads 64 \
  -v
```

For a small smoke test:

```bash
uv run ifstruct-eval \
  --model google/gemini-3-flash-preview \
  --dataset data/test.jsonl \
  --limit 20 \
  --results-file results/smoke.json \
  --n-threads 8 \
  -v
```

You can still override either setting explicitly with `--base-url` or `--api-key`.
`--results-file` writes a JSON artifact with run metadata, aggregate summary stats, and per-sample prompts, responses, and validation results.

## Dataset format

Each JSONL row contains:

- `seed`
- `entity_type`
- `prompt`
- `json_schema`
- `top_level_count`
- `top_level_key`
- `require_wrapper_key`
- `require_code_block`
- `require_no_commentary`
- `output_format`

The test set is the first 2,000 seeds from the `test` split of the current IFStruct taxonomy.
