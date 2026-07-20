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
#  File: evaluate.py                                                          #
#  By: rruiz <rruiz@student.42.fr>                                            #
#  Created: 2026/07/06 11:54:11 by rruiz                                      #
#  Updated: 2026/07/20 09:57:39 by rruiz                                      #
# *************************************************************************** #

import json
import os
from src.models.RagDataset import RagDataset
from src.models.StudentSearchResults import StudentSearchResults
from src.models.AnsweredQuestion import AnsweredQuestion
from pydantic import ValidationError
from src.models.MinimalSource import MinimalSource
from typing import Tuple, Optional, Dict, Any
from src.models.MinimalSearchResults import MinimalSearchResults


def evaluating(student_answer_path: str,
               dataset_path: str,
               k: int
               ) -> None:
    """
    Orchestrates the evaluation of student search results against the dataset.

    Validates the input JSON files, compares the retrieved sources with the
    expected sources, computes the recall metrics at predefined cutoffs,
    and prints the results.

    Args:
        student_answer_path (str): Path to the student's output JSON file.
        dataset_path (str): Path to the ground truth JSON dataset.
        k (int): Maximum cutoff threshold to evaluate.
        max_context_length (int): Maximum length of context considered.

    Raises:
        ValueError: If the loaded data fails Pydantic validation.
    """

    answer_json = load_json_file(student_answer_path)
    dataset_json = load_json_file(dataset_path)

    try:
        answer_data = StudentSearchResults(**answer_json)
        dataset_data = RagDataset(**dataset_json)

    except (ValidationError, TypeError) as e:
        raise ValueError(f'Error, invalid data: {e}')

    print('Student data is valid: True')

    print_dataset_stats(dataset_data, answer_data)

    dataset_dict = {q.question_id: q for q in dataset_data.rag_questions
                    if isinstance(q, AnsweredQuestion)}
    answer_dict = {q.question_id: q for q in answer_data.search_results}

    for question_id in dataset_dict:
        if question_id not in answer_dict:
            print(f'Warning: question {question_id} missing from student'
                  ' answers')

    cutoffs = [1, 3, 5, 10]

    cutoffs = [cutoff for cutoff in cutoffs if cutoff <= k]

    result = {}
    final_question_count = None
    for cutoff in cutoffs:
        recall, question_count = calcul_recall_at_k(dataset_dict,
                                                    answer_dict,
                                                    cutoff)
        if final_question_count is None:
            final_question_count = question_count
        result[cutoff] = recall

    print_result(final_question_count, result)


def load_json_file(path: str) -> Any:
    """
    Loads and parses a JSON file from the given path.

    Args:
        path (str): The file path to load.

    Returns:
        Any: The parsed JSON data as Python objects.

    Raises:
        FileNotFoundError: If the file does not exist at the specified path.
        ValueError: If the file contains invalid JSON data.
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f'Error: The file "{path}" does not exist.')

    if os.path.isdir(path):
        raise IsADirectoryError(f'Error: Expected a file, but "{path}" is a'
                                ' directory.')

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    except json.JSONDecodeError as e:
        raise ValueError(f'Error, invalid JSON in {path}: {e}')


def print_dataset_stats(dataset_data: RagDataset,
                        answer_data: StudentSearchResults) -> None:
    """
    Prints basic statistics about the dataset and the student's submitted
    answers.

    Args:
        dataset_data (RagDataset): The parsed ground truth dataset object.
        answer_data (StudentSearchResults): The parsed student search results
            object.

    Raises:
        ValueError: If the dataset contains no questions with sources.
    """

    questions_count = len(dataset_data.rag_questions)
    print(f'Total number of questions: {questions_count}')

    questions_sources = sum(1 for q in dataset_data.rag_questions
                            if isinstance(q, AnsweredQuestion) and q.sources)
    if questions_sources == 0:
        raise ValueError('Error: no questions found in dataset')

    print(f'Total number of questions with sources: {questions_sources}')

    questions_student_sources = sum(1 for q in answer_data.search_results
                                    if q.retrieved_sources)
    print('Total number of questions with student sources:'
          f' {questions_student_sources}')


def calcul_overlap_ratio(correct: MinimalSource,
                         retrieved: MinimalSource
                         ) -> float:
    """
    Calculates the overlap ratio between a retrieved source and the correct
    source.

    The calculation checks if the retrieved character range overlaps with the
    correct character range within the same file.

    Args:
        correct (MinimalSource): The ground truth source chunk.
        retrieved (MinimalSource): The source chunk retrieved by the student.

    Returns:
        float: The ratio of overlap relative to the correct source's length.
               Returns 0.0 if the files do not match or if there is no overlap.
    """

    if correct.file_path != retrieved.file_path:
        return 0.0

    overlap_start = max(correct.first_character_index,
                        retrieved.first_character_index)
    overlap_end = min(correct.last_character_index,
                      retrieved.last_character_index)

    overlap = overlap_end - overlap_start

    if overlap < 0:
        overlap = 0

    correct_len = correct.last_character_index - correct.first_character_index
    if correct_len <= 0:
        return 0.0

    return overlap / correct_len


def calcul_recall_question(dataset_question: AnsweredQuestion,
                           student_question: MinimalSearchResults | None,
                           cutoff: int
                           ) -> Optional[float]:
    """
    Calculates the recall score for a single question at a specific cutoff.

    A correct source is considered found if there is at least a 5% overlap
    with any of the retrieved sources up to the cutoff rank.

    Args:
        dataset_question (AnsweredQuestion): The ground truth question
            containing the correct sources.
        student_question (MinimalSearchResults | None): The student's retrieved
            results for the question.
        cutoff (int): The maximum number of top retrieved sources to consider.

    Returns:
        Optional[float]: The recall score (number of sources found /
            total correct sources) for the question. Returns None if the
            question has no ground truth sources.
    """

    if not dataset_question.sources:
        return None

    if student_question is None:
        return 0.0

    retrieved = student_question.retrieved_sources[:cutoff]
    if not retrieved:
        return 0.0

    found = 0
    for correct in dataset_question.sources:
        ratios = [calcul_overlap_ratio(correct, r) for r in retrieved]
        if max(ratios) >= 0.05:
            found += 1

    return found / len(dataset_question.sources)


def calcul_recall_at_k(dataset_dict: Dict[str, AnsweredQuestion],
                       answer_dict: Dict[str, MinimalSearchResults],
                       cutoff: int
                       ) -> Tuple[float, int]:
    """
    Calculates the average recall score across all questions at a given cutoff.

    Args:
        dataset_dict (Dict[str, AnsweredQuestion]): A dictionary mapping
            question IDs to the ground truth objects.
        answer_dict (Dict[str, MinimalSearchResults]): A dictionary mapping
            question IDs to the student's results.
        cutoff (int): The top-k threshold for the evaluation.

    Returns:
        Tuple[float, int]: A tuple containing the average recall score and the
            total number of evaluated questions.
    """

    score = 0.0
    question_count = 0

    for question_id, dataset_question in dataset_dict.items():
        student_question = answer_dict.get(question_id)
        result = calcul_recall_question(dataset_question,
                                        student_question,
                                        cutoff)

        if result is None:
            continue
        else:
            score += result
            question_count += 1

    if question_count == 0:
        return (0.0, 0)

    return (score / question_count, question_count)


def print_result(question_count: int | None, result: Dict[int, float]) -> None:
    """
    Displays the final evaluation metrics to the standard output.

    Args:
        question_count (int): The total number of evaluated questions.
        result (Dict[int, float]): A dictionary mapping cutoffs (k) to their
            respective average recall scores.
    """

    print('🎯 Evaluation Results')
    print('========================================')
    print(f'📊 Questions evaluated: {question_count}')
    for cutoff, recall in result.items():
        print(f'📈 Recall@{cutoff}: {recall:.3f} ({int(recall * 100)}%)')
