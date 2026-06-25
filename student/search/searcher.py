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
#  Updated: 2026/06/25 12:44:32 by rruiz                                      #
# *************************************************************************** #

import os
import json
from tqdm import tqdm
from typing import Tuple, List
from student.search.retriever import load_indexes, search
from student.models.StudentSearchResults import StudentSearchResults


def searcher(dataset_path: str, k: int, save_directory: str) -> None:

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

    if not os.path.exists(dataset_path):
        raise FileNotFoundError('Error: The directory'
                                f' {dataset_path} does not'
                                ' exist.')

    with open(dataset_path, 'r') as f:
        dataset = json.load(f)

    datas = []

    for question_data in dataset['rag_questions']:
        datas.append(
            (question_data['question_id'], question_data['question'])
            )

    return datas
