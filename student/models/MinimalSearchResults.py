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
#  File: MinimalSearchResults.py                                              #
#  By: rruiz <rruiz@student.42.fr>                                            #
#  Created: 2026/06/16 10:24:03 by rruiz                                      #
#  Updated: 2026/07/17 10:11:00 by rruiz                                      #
# *************************************************************************** #

from pydantic import BaseModel
from typing import List
from student.models.MinimalSource import MinimalSource


class MinimalSearchResults(BaseModel):
    question_id: str
    question: str
    retrieved_sources: List[MinimalSource]
