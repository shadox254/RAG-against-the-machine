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
#  Updated: 2026/07/10 11:50:48 by rruiz                                      #
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

    if file_type == 'md':
        sep = ['\n\n#', '\n\n', '\n', ' ']
        blocks = md_cutting(content, sep, max_chunk_size, 0)
    else:
        chunk_overlap = max(0, max_chunk_size // 10)
        blocks = py_cutting(content, max_chunk_size, chunk_overlap)

    return blocks


def md_cutting(
        content: str,
        sep: list[str],
        max_chunk_size: int,
        offset: int
        ) -> List[Tuple[int, int]]:
    """
    Splits the content into chunks of maximum size `max_chunk_size` using a
    list of separators.

    Args:
        content (str): The text to be chunked.
        sep (list[str]): The list of separators to use for cutting.
        max_chunk_size (int): The maximum size of each chunk.
        offset (int): The reference index in the original text, used to keep
            track across recursive calls.

    Returns:
        List[Tuple[int, int]]: A list of tuples where the first value is the
            start index of the chunk in the original content, and the second
            value is the end index.
    """

    if len(content) <= max_chunk_size:
        return [(offset, offset + len(content))]

    if len(sep) == 0:
        chunks = []
        pos = 0
        while pos < len(content):
            end = min(pos + max_chunk_size, len(content))
            chunks.append((offset + pos, offset + end))
            pos = end
        return chunks

    current_sep = sep[0]
    other_sep = sep[1:]

    parts = []
    search_from = 0

    while True:
        index = content.find(current_sep, search_from)
        if index == -1:
            parts.append(content[search_from:])
            break
        parts.append(content[search_from:index + len(current_sep)])
        search_from = index + len(current_sep)

    if len(parts) == 1:
        return md_cutting(content, other_sep, max_chunk_size, offset)

    result = []
    current_chunk_len = 0
    current_start = offset
    local_offset = 0

    for part in parts:
        part_len = len(part)

        if current_chunk_len + part_len <= max_chunk_size:
            current_chunk_len += part_len
        else:
            if current_chunk_len > 0:
                result.append(
                    (current_start,
                     current_start + current_chunk_len)
                    )

                local_offset += current_chunk_len
                current_start = offset + local_offset

            if part_len > max_chunk_size:
                sub_chunks = md_cutting(
                    part,
                    other_sep,
                    max_chunk_size,
                    current_start
                    )

                result.extend(sub_chunks)
                local_offset += part_len
                current_start = offset + local_offset
                current_chunk_len = 0
            else:
                current_chunk_len = part_len

    if current_chunk_len > 0:
        result.append((current_start, current_start + current_chunk_len))

    return result


def py_cutting(content: str,
               max_chunk_size: int,
               chunk_overlap: int = 0
               ) -> List[Tuple[int, int]]:
    """
    "Splits the content into chunks of maximum size max_chunk_size using
    LangChain's RecursiveCharacterTextSplitter."

    Args:
        content (str): The text to be chunked.
        max_chunk_size (int): The maximum size of each chunk.
        offset (int): The reference index in the original text, used to keep
            track across recursive calls.
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
