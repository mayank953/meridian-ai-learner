"""RAG question answering: retrieve relevant chunks, then let Gemini answer from them.

    question -> retriever (top matching chunks) -> prompt (chunks + question) -> Gemini -> answer
"""
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import LLMChainExtractor
from langchain_classic.retrievers.multi_query import MultiQueryRetriever
from langchain_core.prompts import ChatPromptTemplate

from logger import GLOBAL_LOGGER as log
from rag.llm import get_llm
from rag.vector_store import get_vector_store

SYSTEM_PROMPT = (
    "You are a helpful assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer the question. "
    "If you don't know the answer based on the context, say that you don't know. "
    "Keep the answer concise and accurate."
    "\n\n"
    "Context: {context}"
)


def build_retriever(retriever_type: str = "similarity"):
    """Pick a retrieval strategy.

    similarity  - the 3 chunks closest in meaning to the question (fast, default)
    multiquery  - Gemini rewrites the question several ways and merges the results
    contextual  - fetch 10 chunks, then Gemini trims each one down to the relevant part
    """
    llm = get_llm()
    store = get_vector_store()

    if retriever_type == "contextual":
        return ContextualCompressionRetriever(
            base_compressor=LLMChainExtractor.from_llm(llm),
            base_retriever=store.as_retriever(search_kwargs={"k": 10}),
        )
    if retriever_type == "multiquery":
        log.info("Using MultiQuery retriever strategy")
        return MultiQueryRetriever.from_llm(
            retriever=store.as_retriever(search_kwargs={"k": 3}), llm=llm
        )
    if retriever_type != "similarity":
        log.warning("Unknown retriever_type, using similarity", retriever_type=retriever_type)
    return store.as_retriever(search_kwargs={"k": 3})


def ask_question(query: str, retriever_type: str = "similarity") -> str:
    """Answer a question using the documents stored in Vector Search."""
    log.info("RAG query received", query=query, retriever_type=retriever_type)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
    ])

    # Chain 1: stuffs the retrieved chunks into the prompt and calls the LLM
    question_answer_chain = create_stuff_documents_chain(get_llm(), prompt)
    # Chain 2: runs the retriever first, then chain 1
    rag_chain = create_retrieval_chain(build_retriever(retriever_type), question_answer_chain)

    response = rag_chain.invoke({"input": query})
    log.info("RAG answer generated", answer=response["answer"])
    return response["answer"]
