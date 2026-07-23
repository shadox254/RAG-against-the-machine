*This project has been created as part of the 42 curriculum by rruiz*

# 🎤 RAG against the machine

## 🏷️ Description

RAG against the machine is a command-line Retrieval-Augmented Generation (RAG) system that answers natural-language questions about vLLM.

Instead of relying solely on the static training data of a language model, the system:

- Ingests the vLLM repository and transforms it into a searchable knowledge base.
- Retrieves the most relevant code snippets or documentation for a given question using BM25.
- Generates a context-aware response using Qwen/Qwen3-0.6B, using only the retrieved context.
- Evaluates the quality of the retrieval step using a recall@k metric against a reference dataset.

## 📝 Instructions

### 📌 Requirements
- Python ≥ 3.10 (project pinned to 3.14) and [`uv`](https://docs.astral.sh/uv/) as package manager
- ~6.5 GB of free disk space

### 👇 Installation
```bash
make install
```
Installs all project dependencies via `uv sync`.

### 👉 Indexing
```bash
uv run python -m src index --max_chunk_size 2000
```
Chunks the vLLM repository, builds the BM25 index, and saves it. `--max_chunk_size` is optional (default: 2000 characters).

### 🛠️ Usage
Each command below can be run standalone via `cd student && uv run python -m src <command>`.

```bash
# Search a single query
uv run python -m src search "How to configure OpenAI server?" --k 10

# Batch search over a dataset
uv run python -m src search_dataset --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json --k 10 --save_directory data/output/search_results

# Answer a single question
uv run python -m src answer "How to configure OpenAI server?" --k 10

# Batch answer generation
uv run python -m src answer_dataset --student_search_results_path data/output/search_results/dataset_docs_public.json --save_directory data/output/search_results_and_answer

# Evaluate retrieval quality against ground truth
uv run python -m src evaluate --student_answer_path data/output/search_results/dataset_docs_public.json --dataset_path data/datasets/AnsweredQuestions/dataset_docs_public.json --k 10
```

### ✂️ Makefile shortcuts
| Rule | Purpose |
|---|---|
| `make install` | Install dependencies |
| `make run` | Run the CLI entry point |
| `make debug` | Run in debug mode (pdb) |
| `make clean` | Remove caches (`__pycache__`, `.mypy_cache`) |
| `make lint` | Run `flake8` and `mypy` |
| `make lint-strict` | Run `flake8` and `mypy --strict` |

## 🏛️ System Architecture
The RAG pipeline is separated into 3 stages:
1. **Index**: Chunks every `.py`, `.md` and `.txt` file in the vLLM repo, tokenizes the resulting corpus, and builds a BM25 index.
2. **Search**: Loads the BM25 index and the chunks generated during indexing, then retrieves the top-k most relevant chunks.
3. **Answer**: Takes the retrieved sources, builds a context string bounded by `max_context_length`, and prompts the model to answer strictly from that context.

## 🧩 Chunking Strategy
Chunking uses LangChain's `RecursiveCharacterTextSplitter`:

| File type | Splitter | Info |
| --------- | -------- | ---- |
| `.md` | `RecursiveCharacterTextSplitter.from_language(Language.MARKDOWN)` | Splits on Markdown structure (headers, code fences, paragraphs). |
| `.py` | `RecursiveCharacterTextSplitter.from_language(Language.PYTHON)` | Splits on Python-aware boundaries (class/def/block level) instead of blind character cuts, so a chunk rarely cuts a function in half. |
| `.txt` | `RecursiveCharacterTextSplitter` | Used for structure-less text files (e.g. `CMakeLists.txt`) that don't benefit from a language-specific separator set. |

For each chunk, the index of the first and last characters of the original file is stored rather than the text of the chunk itself.

**Maximum chunk size**: configurable via the `--max_chunk_size` option on the `index` command (default value used during testing: 2,000 characters).

**Overlap**: `chunk_overlap = max_chunk_size // 13`, applied uniformly to every splitter to preserve some context.

## 🔎 Retrieval method
The project uses BM25 search:

- **Indexing**: the text of each chunk is tokenized and added to the corpus; `bm25s.BM25(corpus=corpus)` builds the index, which is saved in the `data/processed/bm25` directory to enable fast reloading.
- **Querying**: the query is tokenized the same way, and `retriever.retrieve(tokenized_query, k=k)` returns the k segment indices with the highest scores, which are stored as `MinimalSource` objects.

BM25 was chosen over TF-IDF because it naturally handles term frequency saturation and document length normalization, which is better suited to a corpus containing files of highly uneven sizes than classic TF-IDF.

## 📈 Performance Analysis

### 💎 Retrieval quality (recall@k)

| Metric | Docs questions | Code questions | Subject requirement |
| ------ | -------------- | -------------- | ------------------- |
| Recall@1 | 59% | 33% | — |
| Recall@3 | 80% | 50% | — |
| Recall@5 | **86%** | **56%** | 80% (docs) / 50% (code) |
| Recall@10 | 92% | 59% | — |

Both categories meet the subject's minimum bar at k=5 (80% docs / 50% code).

### 🪐 System performance

Measured against the subject's minimum performance thresholds (Chapter VI.1.2):

| Metric | Threshold | Measured |
| ------ | --------- | -------- |
| Indexing time | ≤ 5 min | 00:07.25s |
| Cold start latency (first `answer` call, incl. model loading) | ≤ 60 s | 01:35.41 |
| Warm retrieval throughput (1000 questions, `search` only, index pre-loaded) | ≤ 90 s | - |
| Recall@5 — docs | ≥ 80% | 86% |
| Recall@5 — code | ≥ 50% | 56% |

## 🎨 Design Decisions

**BM25 over embeddings**: sparse lexical retrieval is fast, deterministic, cheap to index/reload, and works well on code and docs, where exact identifier matches (function names, class names, flags) matter more than semantic paraphrasing.

**Character-offset chunks instead of stored text**: keeping only `(file_path, first_character_index, last_character_index)` avoids duplicating the corpus on disk and keeps `data/processed/` small; the original text is re-sliced on demand from `data/raw`.

**Pydantic everywhere**: every object exchanged between stages (chunks, search results, answers) is a pydantic model, so malformed inputs/outputs fail fast with a clear validation error instead of silently corrupting downstream JSON files.

**Strict, context-only prompting**: the system prompt explicitly instructs the model to answer only from the retrieved context and to say "I don't know" otherwise, to keep answers source-grounded and reduce hallucination.

**Context budget by whole source, not truncation**: `build_context` adds retrieved sources one at a time and stops before exceeding `max_context_length`, rather than truncating a source mid-sentence, to keep each included chunk coherent.

## 😐 Challenges Faced

**Recovering exact character offsets after splitting**: LangChain's splitters return chunk text, not offsets. We recover them with `content.find(chunk_text, search_from)`, advancing `search_from` after each match so repeated/near-duplicate chunks don't collide.

**Balancing chunk size vs. recall**: very small chunks improve BM25 precision on function-level questions but hurt recall on documentation questions that span several paragraphs. The configurable `--max_chunk_size` flag and per-file-type splitters were the compromise that best satisfied both the docs and code recall targets.

**Keeping the LLM answer grounded**: since Qwen/Qwen3-0.6B is a small model, it occasionally drifted from the provided context. A strict system prompt plus a low `max_new_tokens` budget helped keep answers short, on-topic, and less prone to hallucination.

## 💡 Example Usage

### 👈 1. Index the repository
```bash
cd student
uv run python -m src index --max_chunk_size 2000
```

Ingestion complete! Indices saved under data/processed/

### 🔎 2. Search a single query
```bash
cd student
uv run python -m src search "How to configure OpenAI server?" --k 5
```
Returns the top-5 most relevant chunks as `MinimalSource` objects (`file_path`, `first_character_index`, `last_character_index`).

### 💬 3. Answer a single question
```bash
cd student
uv run python -m src answer "How to configure OpenAI server?" --k 5
```
Retrieves context, then generates a source-grounded answer with Qwen/Qwen3-0.6B, output as structured JSON following the `MinimalAnswer` model.

### 🗂️ 4. Batch search over a dataset
```bash
cd student
uv run python -m src search_dataset \
  --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json \
  --k 10 \
  --save_directory data/output/search_results
```
Saved student_search_results to data/output/search_results/dataset_docs_public.json

### 🗃️ 5. Batch answer generation
```bash
cd student
uv run python -m src answer_dataset \
  --student_search_results_path data/output/search_results/dataset_docs_public.json \
  --save_directory data/output/search_results_and_answer
```
Loaded 100 questions from data/output/search_results/dataset_docs_public.json
Processed 100 of 100 questions
Saved student_search_results_and_answer to data/output/search_results_and_answer/dataset_docs_public.json

### 6. Evaluate retrieval quality
```bash
uv run python -m student evaluate \
  --student_answer_path data/output/search_results/dataset_docs_public.json \
  --dataset_path data/datasets/AnsweredQuestions/dataset_docs_public.json \
  --k 10
```
### 🧐 Evaluation Results
```
Questions evaluated: 100
Recall@1: 0.590
Recall@3: 0.800
Recall@5: 0.860
Recall@10: 0.920
```

## 📚 Resources

### 📑 Documentation & references
- [Comment fonctionne un RAG](https://www.axopen.com/blog/2025/08/comment-fonctionne-un-rag/)
- [Building CLIs in Python with Fire](https://julienc.io/blog/des_cli_en_python_avec_fire)
- [What is RAG Indexing?](https://www.analyticsvidhya.com/blog/2025/11/what-is-rag-indexing/#h-why-it-matters)
- [tqdm documentation](https://tqdm.github.io/)
- [bm25s documentation](https://bm25s.github.io/)
- [BM25 in a RAG system](https://medium.com/the-dataframe/bm25-in-a-rag-system-the-keyword-search-your-vector-database-is-missing-9b6708cdafff)
- [semchunk](https://github.com/isaacus-dev/semchunk)

### 🤖 AI Usage:
- **Debugging by review**: pointing out bugs without writing the fixes directly.
- **Debugging by testing**: Provide tests that cause crashes or other unintended behavior.
- **README structuring & proofreading**: used Claude to get a section-by-section skeleton of the README based on the subject's requirements, and to proofread/correct grammar and English phrasing on each section. All technical content was written by me.

> ⚠️ **Important Note:** AI was used exclusively as a learning assistant and debugging tool. No code was blindly copied or pasted. Every concept was thoroughly analyzed, refactored, and implemented manually to ensure deep understanding and strict compliance with the project rules.
