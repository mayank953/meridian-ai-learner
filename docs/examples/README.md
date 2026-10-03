# Examples

Six small programs that each show **one idea**. **None needs a Google Cloud account or an API key.** Run them from this folder after installing the requirements (`pip install -r requirements.txt` in the main folder, with `.venv` active).

| File | The idea | Read about it in |
|---|---|---|
| `01_fastapi_hello.py` | Routes, parameters and automatic checking | [09 · FastAPI](../09-fastapi-explained.md) |
| `02_logging_demo.py` | Plain logs vs structured logs, log levels | [10 · Settings and logging](../10-settings-and-logging.md) |
| `03_chunking_demo.py` | How a document is cut into pieces, and overlap | [11 · RAG](../11-rag-explained.md) |
| `04_tool_demo.py` | What an agent actually sees of a tool | [12 · Agents](../12-agents-explained.md) |
| `05_similarity_demo.py` | The maths of "closest meaning" | [11 · RAG](../11-rag-explained.md) |
| `06_settings_demo.py` | Settings from environment variables | [10 · Settings and logging](../10-settings-and-logging.md) |

```bash
cd docs/examples
python 02_logging_demo.py
python 03_chunking_demo.py
python 04_tool_demo.py
python 05_similarity_demo.py
python 06_settings_demo.py
uvicorn 01_fastapi_hello:app --reload --port 8001      # then open http://localhost:8001/docs
```
