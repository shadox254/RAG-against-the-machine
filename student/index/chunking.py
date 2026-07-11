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
#  File: chunking.py                                                          #
#  By: rruiz <rruiz@student.42.fr>                                            #
#  Created: 2026/06/16 13:51:15 by rruiz                                      #
#  Updated: 2026/07/11 09:36:21 by rruiz                                      #
# *************************************************************************** #

from typing import Tuple, List
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language


def chunk(content: str,
          file_type: str,
          max_chunk_size: int
          ) -> List[Tuple[int, int]]:
    """
    Defines the separator to use to split the text into chunks.

    Args:
        content (str): The text to be chunked.
        file_type (str): The extension of the file the text comes from
            ('py' or 'md').
        max_chunk_size (int): The maximum size of each chunk.

    Returns:
        List[Tuple[int, int]]: A list of tuples where the first value
            is the start index of the chunk in the original content, and the
            second value is the end index.
    """

    chunk_overlap = max(0, max_chunk_size // 13)
    if file_type == 'md':
        blocks = md_cutting(content, max_chunk_size, chunk_overlap)
    else:
        blocks = py_cutting(content, max_chunk_size, chunk_overlap)

    return blocks


def md_cutting(content: str,
                 max_chunk_size: int,
                 chunk_overlap: int = 0
                 ) -> List[Tuple[int, int]]:
    """
    Splits the content into chunks of maximum size max_chunk_size using
    LangChain's RecursiveCharacterTextSplitter.

    Args:
        content (str): The text to be chunked.
        max_chunk_size (int): The maximum size of each chunk.
        chunk_overlap (int): The number of characters of intentional overlap
            between two consecutive chunks. Defaults to 0 (no overlap).

    Returns:
        List[Tuple[int, int]]: A list of tuples where the first value is the
            start index of the chunk in the original content, and the second
            value is the end index.
    """

    result = []

    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.MARKDOWN,
        chunk_size=max_chunk_size,
        chunk_overlap=chunk_overlap
    )

    raw_chunks = splitter.split_text(content)
    search_from = 0
    for chunk_text in raw_chunks:
        start = content.find(chunk_text, search_from)
        end = start + len(chunk_text)

        result.append((start, end))

        search_from = max(0, end - chunk_overlap)

    return result


def py_cutting(content: str,
               max_chunk_size: int,
               chunk_overlap: int = 0
               ) -> List[Tuple[int, int]]:
    """
    Splits the content into chunks of maximum size max_chunk_size using
    LangChain's RecursiveCharacterTextSplitter.

    Args:
        content (str): The text to be chunked.
        max_chunk_size (int): The maximum size of each chunk.
        chunk_overlap (int): The number of characters of intentional overlap
            between two consecutive chunks. Defaults to 0.


    Returns:
        List[Tuple[int, int]]: A list of tuples where the first value is the
            start index of the chunk in the original content, and the second
            value is the end index.
    """

    result = []

    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON,
        chunk_size=max_chunk_size,
        chunk_overlap=chunk_overlap
    )

    raw_chunks = splitter.split_text(content)
    last_index = 0
    for chunk_text in raw_chunks:
        start = content.find(chunk_text, last_index)
        end = start + len(chunk_text)

        result.append((start, end))

        last_index = max(0, end - chunk_overlap)

    return result
