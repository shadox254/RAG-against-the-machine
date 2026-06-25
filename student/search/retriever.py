# *************************************************************************** #
#                                                                             #
#     |\      _,,,---,,_                                                      #
#     /,`.-'`'    -.  ;-;;,_                                                  #
#    |,4-  ) )-,_. ,\ (  `'-'                                                 #
#   '---''(_/--'  `-'\_)         __..--''``---....___   _..._    __           #
#                            _.-'    .-/";  `        ``<._  ``.''_ `.         #
#                        _.-' _..--.'_    \                    `( ) )         #
#                       (_..-' // (< _     ;_..__               ; `'          #
#                                  `-._,_)' // / ``--...____..-'              #
#                                                                             #
# *************************************************************************** #
#  File: retriever.py                                                         #
#  By: rruiz <rruiz@student.42.fr>                                            #
#  Created: 2026/06/22 17:31:51 by rruiz                                      #
#  Updated: 2026/06/24 09:49:19 by rruiz                                      #
# *************************************************************************** #

import bm25s
import json
import os
from student.models.MinimalSearchResults import MinimalSearchResults
from student.models.StudentSearchResults import StudentSearchResults
from student.models.MinimalSource import MinimalSource
from typing import Tuple, Any


def load_indexes() -> Tuple[bm25s.BM25, bm25s.BM25, Any, Any]:
    """
    Loads BM25 indexes and chunk files.

    Returns:
        tuple: (md_retriever, py_retriever, chunks_md, chunks_py)

    Raises:
        FileNotFoundError: If index directories or chunk files do not exist.
    """

    md_dir = 'data/processed/bm25_md'
    py_dir = 'data/processed/bm25_py'
    md_chunks_f = 'data/processed/chunks/chunks_md.json'
    py_chunks_f = 'data/processed/chunks/chunks_py.json'

    if not os.path.exists(md_dir):
        raise FileNotFoundError('Error: The directory "data/processed/bm25_md"'
                                ' does not exist. Try "uv run python -m'
                                ' student index --max_chunk_size int" then'
                                ' try the command again.')

    if not os.path.exists(py_dir):
        raise FileNotFoundError('Error: The directory "data/processed/bm25_py"'
                                ' does not exist. Try "uv run python -m'
                                ' student index --max_chunk_size int" then'
                                ' try the command again.')

    if not os.path.exists(md_chunks_f) or not os.path.exists(py_chunks_f):
        raise FileNotFoundError('Error: Chunk files do not exist. Try'
                                ' "uv run python -m student index'
                                ' --max_chunk_size int" then try the command'
                                ' again.')

    md = bm25s.BM25.load(save_dir=bm25s.Path(md_dir))
    py = bm25s.BM25.load(save_dir=bm25s.Path(py_dir))

    with open(md_chunks_f, 'r') as f:
        chunks_md = json.load(f)

    with open(py_chunks_f, 'r') as f:
        chunks_py = json.load(f)

    return (md, py, chunks_md, chunks_py)


def search(
    query: str,
    k: int,
    indexes: Tuple[bm25s.BM25, bm25s.BM25, Any, Any],
    question_id: str = 'q1'
) -> MinimalSearchResults:
    """
    Queries the BM25 indexes to retrieve the most relevant text segments.

    Args:
        query (str): The search query.
        k (int): The maximum number of results to return.
        indexes (tuple): Output of load_indexes().
        question_id (str): The ID of the question being searched.

    Returns:
        MinimalSearchResults: The retrieved sources for this query.
    """

    md, py, chunks_md, chunks_py = indexes

    tokenized_query = bm25s.tokenize(query)

    md_results = md.retrieve(tokenized_query, k=k)
    py_results = py.retrieve(tokenized_query, k=k)

    all_results = []
    for doc_index, score in zip(md_results.documents[0], md_results.scores[0]):
        all_results.append((score, chunks_md[doc_index]))

    for doc_index, score in zip(py_results.documents[0], py_results.scores[0]):
        all_results.append((score, chunks_py[doc_index]))

    all_results.sort(key=lambda x: x[0], reverse=True)
    all_results = all_results[:k]

    sources = [
        MinimalSource(
            file_path=chunk['file_path'],
            first_character_index=chunk['first_character_index'],
            last_character_index=chunk['last_character_index']
        )
        for _, chunk in all_results
    ]

    return MinimalSearchResults(
        question_id=question_id,
        question=query,
        retrieved_sources=sources
    )


def retrieving(query: str, k: int) -> str:
    """
    Convenience wrapper for single query search.

    Args:
        query (str): The search query.
        k (int): The maximum number of results to return.

    Returns:
        str: A JSON-formatted string of StudentSearchResults.
    """

    indexes = load_indexes()
    result = search(query, k, indexes)

    return StudentSearchResults(
        search_results=[result],
        k=k
    ).model_dump_json(indent=2)
