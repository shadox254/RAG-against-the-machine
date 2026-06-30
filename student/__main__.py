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
#  File: __main__.py                                                          #
#  By: rruiz <rruiz@student.42.fr>                                            #
#  Created: 2026/06/15 15:13:42 by rruiz                                      #
#  Updated: 2026/06/30 09:58:35 by rruiz                                      #
# *************************************************************************** #

import fire
import sys
from student.index.indexing import ingesting
from student.search.retriever import retrieving
from student.search.searcher import searcher


def index(max_chunk_size: int) -> None:
    try:
        int(max_chunk_size)
    except TypeError:
        pass
    ingesting(max_chunk_size)
    print('Ingestion complete! Indices saved under data/processed/')


def search(query: str, k: int = 1) -> None:
    try:
        int(k)
        if int(k) <= 0:
            raise ValueError('Error, k must be a integer greater than 0.')
    except ValueError:
        raise ValueError('Error, k must be a integer greater than 0.')
    result = retrieving(query, k)
    print(result)


def search_dataset(
        dataset_path: str,
        k: int = 1,
        save_directory: str = 'data/output/search_results'
        ) -> None:
    searcher(dataset_path, k, save_directory)


def answer(question: str, k: int) -> None:
    print('Answer a single question with context')


def answer_dataset() -> None:
    print('Generate answers from search results')


def evaluate() -> None:
    print('Evaluate search results against ground truth')


if __name__ == "__main__":
    try:
        fire.Fire()

    except (FileNotFoundError, ValueError) as e:
        print(e)

    except KeyboardInterrupt:
        print('Program interrupt by user.', file=sys.stderr)

    except Exception as e:
        print(f'Unexpected error: {e}', file=sys.stderr)
