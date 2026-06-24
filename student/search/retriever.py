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


def retrieving(query: str, k: int) -> str:
    """
    Queries the BM25 indexes (Markdown and Python) to retrieve the most
        relevant text segments for a given query, then merges and sorts the
        results.

    Args:
        query (str): The search query provided by the user.
        k (int): The maximum number of final results to return after merging.

    Returns:
        str: A JSON-formatted string containing the results structured
             according to the StudentSearchResults model.
    """

    md_dir = 'data/processed/bm25_md'
    py_dir = 'data/processed/bm25_py'
    md_chunks_f = 'data/processed/chunks/chunks_md.json'
    py_chunks_f = 'data/processed/chunks/chunks_py.json'

    if not os.path.exists(md_dir):
        raise FileNotFoundError('Error: The directory “data/processed/bm25_md”'
                                ' does not exist. Try “uv run python -m'
                                ' student index --max_chunk_size int” then'
                                ' try the command again.')

    if not os.path.exists(py_dir):
        raise FileNotFoundError('Error: The directory “data/processed/bm25_py”'
                                ' does not exist. Try “uv run python -m'
                                ' student index --max_chunk_size int” then'
                                ' try the command again.')

    if not os.path.exists(md_chunks_f) or not os.path.exists(py_chunks_f):
        raise FileNotFoundError('Error: Chunk files does not exist. Try'
                                ' “uv run python -m student index'
                                ' --max_chunk_size int” then try the command'
                                ' again.')

    md_path = bm25s.Path(md_dir)
    py_path = bm25s.Path(py_dir)

    md = bm25s.BM25.load(save_dir=md_path)
    py = bm25s.BM25.load(save_dir=py_path)

    tokenized_query = bm25s.tokenize(query)

    md_results = md.retrieve(tokenized_query, k=k)
    py_results = py.retrieve(tokenized_query, k=k)

    with open(md_chunks_f, 'r') as f:
        chunks_md = json.load(f)

    with open(py_chunks_f, 'r') as f:
        chunks_py = json.load(f)

    all_result = []
    for doc_index, score in zip(md_results.documents[0], md_results.scores[0]):
        chunk = chunks_md[doc_index]
        all_result.append((score, chunk))

    for doc_index, score in zip(py_results.documents[0], py_results.scores[0]):
        chunk = chunks_py[doc_index]
        all_result.append((score, chunk))

    #
    all_result.sort(key=lambda x: x[0], reverse=True)
    all_result = all_result[:k]

    sources = []
    minimal_result = []

    for e in all_result:
        chunk_infos = e[1]
        sources.append(MinimalSource(
            file_path=chunk_infos['file_path'],
            first_character_index=chunk_infos['first_character_index'],
            last_character_index=chunk_infos['last_character_index'])
            )

    minimal_result.append(MinimalSearchResults(
        question_id='q1',
        question=query,
        retrieved_sources=sources
    ))

    result = StudentSearchResults(
        search_results=minimal_result,
        k=k
    )

    return result.model_dump_json(indent=2)
