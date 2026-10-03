"""See exactly how a document is cut into chunks. No cloud account needed.

Run:    python 03_chunking_demo.py

Change CHUNK_SIZE and CHUNK_OVERLAP and run again. Notice how the overlap
repeats the end of one chunk at the start of the next, so an idea that falls
on the boundary is not lost.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = 200      # the project uses 1000
CHUNK_OVERLAP = 40    # the project uses 100

text = (
    "Aldermoor Industries is a fictional manufacturer of industrial packaging machinery. "
    "Vendors with a credit score of 75 or higher are low risk and receive Net-45 payment terms. "
    "Vendors scoring 50 to 74 are moderate risk and require a deposit or a letter of credit. "
    "Vendors scoring below 50 are high risk and require full prepayment plus a bank guarantee. "
    "Purchases above EUR 250,000 need Department Head sign-off, and purchases above "
    "EUR 1,000,000 need CFO and Management Board approval."
)

splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
chunks = splitter.split_text(text)

print(f"{len(text)} characters -> {len(chunks)} chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})\n")
for i, chunk in enumerate(chunks, 1):
    print(f"--- chunk {i} ({len(chunk)} chars) ---")
    print(chunk)
    print()
