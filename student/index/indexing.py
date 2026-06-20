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
#  File: indexing.py                                                          #
#  By: rruiz <rruiz@student.42.fr>                                            #
#  Created: 2026/06/16 12:57:52 by rruiz                                      #
#  Updated: 2026/06/20 15:00:46 by rruiz                                      #
# *************************************************************************** #

import os
import json
import bm25s
from typing import Tuple, List
from tqdm import tqdm
from student.index.chunking import chunk


def ingesting(max_chunk_size: int) -> None:
    """
    Handles the indexing logic: iterates through the files to process,
        splits them into chunks, indexes them, and saves the output in a
        properly formatted .json file.

    Args:
        max_chunk_size (int): The maximum size of each chunk.
    """

    src_dir = 'data/raw/vllm-0.10.1'
    doc_list = find_doc(src_dir)

    try:
        max_chunk_size = int(max_chunk_size)
        md_chunks = []
        py_chunks = []

        corpus_md = []
        corpus_py = []

        progress_bar = tqdm(
            total=len(doc_list) + 2,
            desc='Chunking files from vllm',
            bar_format='{desc}: {percentage:3.0f}% |{bar}| {n}/{total} '
            '{elapsed_s:2.2f}s elapsed'
            )

        for file, file_ext in doc_list:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            chunks = chunk(content, file_ext, max_chunk_size)
            for first_index, last_index in chunks:
                text = content[first_index:last_index]
                chunk_data = {
                    'file_path': file,
                    'first_character_index': first_index,
                    'last_character_index': last_index
                }
                if file_ext == 'md':
                    md_chunks.append(chunk_data)
                    corpus_md.append(text)
                else:
                    py_chunks.append(chunk_data)
                    corpus_py.append(text)
            progress_bar.update(1)

        progress_bar.set_description('Tokenizing md')
        md_tokens = bm25s.tokenize(corpus_md)
        retriever = bm25s.BM25(corpus=corpus_md)
        retriever.index(md_tokens)
        retriever.save('data/processed/bm25_md')
        progress_bar.update(1)

        progress_bar.set_description('Tokenizing py')
        py_tokens = bm25s.tokenize(corpus_py)
        retriever = bm25s.BM25(corpus=corpus_py)
        retriever.index(py_tokens)
        retriever.save('data/processed/bm25_py')
        progress_bar.update(1)

        progress_bar.close()

        output_dir = 'data/processed/chunks'
        os.makedirs(output_dir, exist_ok=True)

        if len(md_chunks) > 0:
            output_file = 'chunks_md.json'
            with open(os.path.join(output_dir, output_file), 'w') as f:
                json.dump(md_chunks, f, indent=4)

        if len(py_chunks) > 0:
            output_file = 'chunks_py.json'
            with open(os.path.join(output_dir, output_file), 'w') as f:
                json.dump(py_chunks, f, indent=4)

    except Exception as e:
        print(f'Error during the indexing: {e}')
        exit()

    finally:
        progress_bar.close()


def find_doc(directory: str) -> List[Tuple[str, str]]:
    """
    Finds all .md or .py files within a given directory.

    Args:
        directory (str): The root directory to search in.

    Returns:
        List[Tuple[str, str]]: A list of tuples containing the file path and
            its extension.
    """

    doc_list = []

    for element in os.walk(directory):
        root = element[0]
        for file in element[2]:
            ext = file.split('.')[-1]
            if ext == 'py' or ext == 'md':
                path_file = os.path.join(root, file)
                doc_list.append((path_file, ext))

    return doc_list
