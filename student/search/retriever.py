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
#  Updated: 2026/07/03 10:11:30 by rruiz                                      #
# *************************************************************************** #

import bm25s
import json
import os
from student.models.MinimalSearchResults import MinimalSearchResults
from student.models.StudentSearchResults import StudentSearchResults
from student.models.MinimalSource import MinimalSource
from typing import Tuple, Any


def load_indexes() -> Tuple[bm25s.BM25, Any]:
    """
    Loads BM25 indexes and chunk files.

    Returns:
        tuple: (md_retriever, py_retriever, chunks_md, chunks_py)

    Raises:
        FileNotFoundError: If index directories or chunk files do not exist.
    """

    index_dir = 'data/processed/bm25'
    chunks_f = 'data/processed/chunks/chunks.json'

    if not os.path.exists(index_dir):
        raise FileNotFoundError('Error: The directory "data/processed/bm25"'
                                ' does not exist. Try "uv run python -m'
                                ' student index --max_chunk_size int" then'
                                ' try the command again.')

    if not os.path.exists(chunks_f):
        raise FileNotFoundError("""Error: Chunk files do not exist. Try "uv
                                 run python -m student index --max_chunk_size
                                 int" then try the command again.""")

    retriever = bm25s.BM25.load(save_dir=bm25s.Path(index_dir))

    with open(chunks_f, 'r') as f:
        chunks = json.load(f)

    return (retriever, chunks)


def search(
    query: str,
    k: int,
    indexes: Tuple[bm25s.BM25, Any],
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

    retriever, chunks = indexes

    tokenized_query = bm25s.tokenize(query)

    results = retriever.retrieve(tokenized_query, k=k)

    sources = []
    for doc_index in results.documents[0]:
        sources.append(
            MinimalSource(
                file_path=chunks[doc_index]['file_path'],
                first_character_index=(
                    chunks[doc_index]['first_character_index']),
                last_character_index=chunks[doc_index]['last_character_index']
                )
                )

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
