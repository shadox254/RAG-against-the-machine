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
#  File: StudentSearchResults.py                                              #
#  By: rruiz <rruiz@student.42.fr>                                            #
#  Created: 2026/06/16 10:26:08 by rruiz                                      #
#  Updated: 2026/06/16 11:44:37 by rruiz                                      #
# *************************************************************************** #

from pydantic import BaseModel
from typing import List
from student.models.MinimalSearchResults import MinimalSearchResults


class StudentSearchResults(BaseModel):
    search_results: List[MinimalSearchResults]
    k: int
