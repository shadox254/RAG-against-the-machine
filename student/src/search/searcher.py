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
#  File: searcher.py                                                          #
#  By: rruiz <rruiz@student.42.fr>                                            #
#  Created: 2026/06/25 12:44:32 by rruiz                                      #
#  Updated: 2026/07/18 16:49:18 by rruiz                                      #
# *************************************************************************** #

import os
import json
from tqdm import tqdm
from typing import Tuple, List
from src.search.retriever import load_indexes, search
from src.models.StudentSearchResults import StudentSearchResults


def searcher(dataset_path: str, k: int, save_directory: str) -> None:
    """
    Processes a dataset of questions, retrieves the top 'k' sources for each,
    and saves the results as a JSON file.

    Args:
        dataset_path (str): Path to the JSON file containing the questions.
        k (int): Number of documents/sources to retrieve for each question.
        save_directory (str): Path to the directory where the results will be
            saved.
    """

    datas = read_dataset(dataset_path)
    indexes = load_indexes()

    results = []

    progress_bar = tqdm(
            total=len(datas),
            desc='Processing questions',
            bar_format='{desc}: {percentage:3.0f}% |{bar}| {n}/{total} '
            '{elapsed_s:2.2f}s elapsed'
            )

    try:
        for data in datas:
            question_id, question = data
            results.append(search(question, k, indexes, question_id))
            progress_bar.update(1)

    finally:
        progress_bar.close()

    result = StudentSearchResults(
        search_results=results,
        k=k
        )

    os.makedirs(save_directory, exist_ok=True)
    save_path = os.path.join(save_directory, os.path.basename(dataset_path))

    with open(save_path, 'w+') as f:
        f.write(result.model_dump_json(indent=2))

    print(f'Saved student_search_results to {save_path}')


def read_dataset(dataset_path: str) -> List[Tuple[str, str]]:
    """
    Reads the dataset JSON file and extracts question IDs and text.

    Args:
        dataset_path (str): Path to the dataset file.

    Returns:
        List[Tuple[str, str]]: A list of tuples, where each tuple contains
            (question_id, question).

    Raises:
        FileNotFoundError: If the specified dataset_path does not exist.
        IsADirectoryError: If the specified dataset_path is a directory.
        ValueError: If the JSON structure is invalid or contains invalid data.
    """

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f'Error: The file "{dataset_path}" does not'
                                ' exist.')

    if os.path.isdir(dataset_path):
        raise IsADirectoryError(f'Error: Expected a file, but "{dataset_path}"'
                                ' is a directory.')

    try:
        with open(dataset_path, 'r') as f:
            dataset = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f'Error: Invalid JSON in file "{dataset_path}": {e}')

    if not isinstance(dataset, dict):
        raise ValueError('Error: Expected JSON object, but got'
                         f' {type(dataset).__name__}.')

    if 'rag_questions' not in dataset:
        raise ValueError('Error: JSON must contain "rag_questions" key.')

    if not isinstance(dataset['rag_questions'], list):
        raise ValueError('Error: "rag_questions" must be a list,'
                         f' not {type(dataset["rag_questions"]).__name__}.')

    datas = []
    seen_ids = set()

    for idx, question_data in enumerate(dataset['rag_questions']):

        if not isinstance(question_data, dict):
            raise ValueError(f'Error: Question at index {idx} must be an'
                             ' object, but got'
                             f' {type(question_data).__name__}.')

        if 'question_id' not in question_data:
            raise ValueError(f'Error: Question at index {idx} is missing '
                             '"question_id" field.')

        if 'question' not in question_data:
            raise ValueError(f'Error: Question at index {idx} is missing'
                             ' "question" field.')

        question_id = question_data['question_id']
        question = question_data['question']

        if (not question or not isinstance(question, str) or
                not question.strip()):
            raise ValueError(f'Error: Question at index {idx} has empty or'
                             ' invalid "question" field.')

        if question_id in seen_ids:
            raise ValueError(f'Error: Duplicate question_id "{question_id}"'
                             ' found at index {idx}.')

        seen_ids.add(question_id)
        datas.append((question_id, question))

    return datas
