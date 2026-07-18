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
#  File: answering_dataset.py                                                 #
#  By: rruiz <rruiz@student.42.fr>                                            #
#  Created: 2026/07/03 10:06:55 by rruiz                                      #
#  Updated: 2026/07/18 16:48:19 by rruiz                                      #
# *************************************************************************** #

from src.models.StudentSearchResults import StudentSearchResults
from src.models.MinimalAnswer import MinimalAnswer
from src.models.StudentSearchResultsAndAnswer import (
    StudentSearchResultsAndAnswer)
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Any, Tuple
import os
import json
from src.answer.answering import build_context, answering
from tqdm import tqdm


def load_model(model_name: str) -> Tuple[Any, Any]:
    """
    Load the specified tokenizer and causal language model from Hugging Face.

    Args:
        model_name (str): The name or path of the pre-trained model to load.

    Returns:
        Tuple[Any, Any]: A tuple containing the loaded tokenizer and model.
    """

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model: Any = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto"
    )

    return tokenizer, model


def answering_dataset(
        student_search_results_path: str,
        save_directory: str,
        k: int,
        max_context_length: int,
        model_name: str = 'Qwen/Qwen3-0.6B') -> None:
    """
    Process a search results dataset to generate answers using a language
    model.

    Loads questions and sources from a JSON file, uses the model to generate
    a response for each question, and saves the compiled results.

    Args:
        student_search_results_path (str): Path to the JSON file containing
            the search results.
        save_directory (str): Destination directory where the output file
            will be saved.
        k (int): Number of retrieved sources per question.
        model_name (str, optional): Name of the model to use. Defaults to
            "Qwen/Qwen3-0.6B".
    """

    if not os.path.exists(student_search_results_path):
        raise FileNotFoundError(f'Error: The file'
                                f'" {student_search_results_path}" does not'
                                ' exist.')

    # Check if it's a directory instead of a file
    if os.path.isdir(student_search_results_path):
        raise IsADirectoryError('Error: Expected a file, but '
                                f'"{student_search_results_path}" is a'
                                ' directory.')

    try:
        with open(student_search_results_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        student_search_result = StudentSearchResults(**content)

    except json.JSONDecodeError as e:
        raise ValueError('Error: Invalid JSON in file '
                         f'"{student_search_results_path}": {e}')

    except TypeError as e:
        raise ValueError('Error: Invalid data structure in file '
                         f'"{student_search_results_path}": {e}')

    print(f'Loaded {len(student_search_result.search_results)} questions from'
          f' {student_search_results_path}')

    if os.path.exists(save_directory) and not os.path.isdir(save_directory):
        raise IsADirectoryError(f'Error: "{save_directory}" exists but is a'
                                ' file, not a directory.')

    try:
        tokenizer, model = load_model(model_name)
    except Exception as e:
        raise ValueError(f'Error loading model "{model_name}": {e}')

    search_results = []

    progress_bar = tqdm(
        total=len(student_search_result.search_results),
        desc='Processing questions',
        bar_format='{desc}: {percentage:3.0f}% |{bar}| {n}/{total} '
        '{elapsed_s:2.2f}s elapsed'
        )

    try:
        for search in student_search_result.search_results:
            try:
                context = build_context(
                    search.retrieved_sources,
                    max_context_length
                    )
                answer = answering(context, search.question, tokenizer, model)
            except (FileNotFoundError, OSError) as e:
                print(f'Warning: skipping question {search.question_id} '
                      f'(source unreadable): {e}')
                progress_bar.update(1)
                continue

            search_results.append(
                MinimalAnswer(
                    question_id=search.question_id,
                    question=search.question,
                    retrieved_sources=search.retrieved_sources,
                    answer=answer
                )
            )
            progress_bar.update(1)
    finally:
        progress_bar.close()

    print(f'Processed {len(search_results)} of'
          f' {len(student_search_result.search_results)} questions')

    result = StudentSearchResultsAndAnswer(
        search_results=search_results,
        k=k
    )

    os.makedirs(save_directory, exist_ok=True)
    save_path = os.path.join(
        save_directory,
        os.path.basename(student_search_results_path)
        )

    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(result.model_dump_json(indent=2))

    print(f'Saved student_search_results_and_answer to {save_path}')
