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
#  Updated: 2026/06/19 11:28:18 by rruiz                                      #
# *************************************************************************** #

import fire
import sys
from student.index.indexing import ingesting


def index(max_chunk_size: int) -> None:
    ingesting(max_chunk_size)
    print('Ingestion complete! Indices saved under data/processed/')


def search() -> None:
    print('search for a single query')


def search_dataset(
        student_search_results_path: str,
        save_directory: str
        ) -> None:
    print('Process multiple questions and output search results')


def answer(question: str, k: int | None = None) -> None:
    print('Answer a single question with context')


def answer_dataset() -> None:
    print('Generate answers from search results')


def evaluate() -> None:
    print('Evaluate search results against ground truth')


if __name__ == "__main__":
    try:
        fire.Fire()
    except KeyboardInterrupt:
        print('Program interrupt by user.', file=sys.stderr)

    except Exception as e:
        print(f'Unexpected error: {e}', file=sys.stderr)
