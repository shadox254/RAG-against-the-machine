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
from student.evaluate.evaluate import evaluating
from json import JSONDecodeError
from pydantic import ValidationError


def index(max_chunk_size: int) -> None:
    """
    Triggers the ingestion and indexing of the repository files.

    Args:
        max_chunk_size (int): The maximum number of characters allowed per
            chunk.
    """

    if not isinstance(max_chunk_size, int):
        raise TypeError('Error, max_chunk_size must be an integer.')

    if max_chunk_size <= 10 or max_chunk_size > 10000:
        raise ValueError('Error: max_chunk_size must be greater than 10 and'
                         ' less than or equal to 10000.')

    ingesting(max_chunk_size)
    print('Ingestion complete! Indices saved under data/processed/')


def search(query: str, k: int = 1) -> None:
    """
    Searches the indexed knowledge base for a single query.

    Args:
        query (str): The search query provided by the user.
        k (int, optional): The number of top results to retrieve. Defaults to
            1.

    Raises:
        ValueError: If k is not an integer or not between 1 and 20 included.
    """

    if not isinstance(k, int):
        raise TypeError('Error, k must be an integer.')

    if k <= 0 or k > 20:
        raise ValueError('Error, k must be greater than 0 and'
                         ' less than or equal to 20.')

    result = retrieving(query, k)
    print(result)


def search_dataset(
        dataset_path: str,
        k: int = 1,
        save_directory: str = 'data/output/search_results'
        ) -> None:
    """
    Processes multiple questions from a JSON dataset and outputs the search
    results.

    Args:
        dataset_path (str): The file path to the input JSON dataset.
        k (int, optional): The number of top results to retrieve per question.
            Defaults to 1.
        save_directory (str, optional): The directory where the search results
            will be saved. Defaults to 'data/output/search_results'.

    Raises:
        ValueError: If k is not between 1 and 20 included.
    """

    if k <= 0 or k > 20:
        raise ValueError('Error, k must be an integer between 0 excluded and'
                         ' 20 included')

    searcher(dataset_path, k, save_directory)


def answer(query: str,
           k: int = 1,
           model_name: str = 'Qwen/Qwen3-0.6B',
           max_context_length: int = 2000
           ) -> None:
    """
    Answers a single question using a Large Language Model with retrieved
    context.

    Args:
        query (str): The question to answer.
        k (int, optional): The number of sources to retrieve for context.
            Defaults to 1.
        model_name (str, optional): The name of the LLM to use.
            Defaults to 'Qwen/Qwen3-0.6B'.
        max_context_length (int, optional): The maximum length of the context
            passed to the model. Defaults to 2000.

    Raises:
        ValueError: If k is not between 1 and 20 included.
    """

    if k <= 0 or k > 20:
        raise ValueError('Error, k must be an integer between 0 excluded and'
                         ' 20 included')

    answerer(query, k, max_context_length, model_name)


def answer_dataset(
        student_search_results_path: str,
        save_directory: str,
        k: int = 1,
        max_context_length: int = 2000,
        model_name: str = 'Qwen/Qwen3-0.6B'
        ) -> None:
    """
    Generates answers for a dataset of questions based on previously retrieved
    search results.

    Args:
        student_search_results_path (str): The path to the JSON file containing
            the search results.
        save_directory (str): The directory where the final answers will be
            saved.
        k (int, optional): The number of sources to consider per question.
            Defaults to 1.
        max_context_length (int, optional): The maximum allowed context length
            for the LLM. Defaults to 2000.
        model_name (str, optional): The name of the LLM to use.
            Defaults to 'Qwen/Qwen3-0.6B'.

    Raises:
        ValueError: If k is not between 1 and 20 included.
    """

    if k <= 0 or k > 20:
        raise ValueError('Error, k must be an integer between 0 excluded and'
                         ' 20 included')

    answering_dataset(
        student_search_results_path,
        save_directory,
        k,
        max_context_length,
        model_name
        )


def evaluate(
        student_answer_path: str,
        dataset_path: str,
        k: int = 1,
        max_context_length: int = 2000
        ) -> None:
    """
    Evaluates the search results against the ground truth using the
    recall@k metric.

    Args:
        student_answer_path (str): The path to the JSON file containing the
            student's search results.
        dataset_path (str): The path to the JSON file containing the ground
            truth dataset.
        k (int, optional): The cutoff rank for evaluation. Defaults to 1.
        max_context_length (int, optional): The maximum allowed context length
            (currently unused in metric). Defaults to 2000.

    Raises:
        ValueError: If k is not between 1 and 20 included.
    """

    if k <= 0 or k > 20:
        raise ValueError('Error, k must be an integer between 0 excluded and'
                         ' 20 included')

    evaluating(student_answer_path, dataset_path, k, max_context_length)


if __name__ == "__main__":
    try:
        fire.Fire()

    except (FileNotFoundError, ValueError, TypeError,
            ValidationError, JSONDecodeError) as e:
        print(e)

    except KeyboardInterrupt:
        print('Program interrupt by user.', file=sys.stderr)

    except Exception as e:
        print(f'Unexpected error: {e}', file=sys.stderr)
