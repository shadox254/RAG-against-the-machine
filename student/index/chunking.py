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
#  Updated: 2026/06/19 16:07:32 by rruiz                                      #
# *************************************************************************** #

from typing import Tuple, List


def chunk(content: str,
          file_type: str,
          max_chunk_size: int
          ) -> List[Tuple[int, int]]:

    if file_type == 'md':
        sep = ['\n\n#', '\n\n', '\n', ' ']
    else:
        sep = ['\nimport', '\nclass ', '\ndef ', '\n\n', '\n', ' ']

    blocks = cutting(content, sep, max_chunk_size, 0)

    return blocks


def cutting(
        content: str,
        sep: list[str],
        max_chunk_size: int,
        offset: int
        ) -> List[Tuple[int, int]]:

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

    cut_points = []
    search_from = 0

    while True:
        index = content.find(current_sep, search_from)
        if index == -1:
            break
        cut_points.append(index)
        search_from = index + len(current_sep)

    if len(cut_points) == 0:
        return cutting(content, other_sep, max_chunk_size, offset)

    parts = []
    start = 0
    for point in cut_points:
        parts.append(content[start:point])
        start = point
    parts.append(content[start:])

    result = []
    local_pos = 0
    for part in parts:
        offset_part = offset + local_pos
        if len(part) > 0:
            if len(part) <= max_chunk_size:
                result.append((offset_part, offset_part + len(part)))
            else:
                result.extend(cutting(part, other_sep, max_chunk_size,
                                      offset_part))
            local_pos += len(part)

    return result
