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
#  Updated: 2026/07/04 15:21:47 by rruiz                                      #
# *************************************************************************** #

import fire
import sys
from student.index.indexing import ingesting
from student.search.retriever import retrieving
from student.search.searcher import searcher
from student.answer.answering import answerer
from student.answer.answering_dataset import answering_dataset


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


def answer(query: str, k: int = 1) -> None:
    answerer(query, k)


def answer_dataset(
        student_search_results_path: str,
        save_directory: str,
        k: int = 1,
        model_name: str | None = None) -> None:

    if model_name is None:
        answering_dataset(
            student_search_results_path,
            save_directory,
            k
            )

    else:
        answering_dataset(
            student_search_results_path,
            save_directory,
            k,
            model_name
            )

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
