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
#  File: StudentSearchResultsAndAnswer.py                                     #
#  By: rruiz <rruiz@student.42.fr>                                            #
#  Created: 2026/06/16 10:27:09 by rruiz                                      #
#  Updated: 2026/06/16 13:14:43 by rruiz                                      #
# *************************************************************************** #

from typing import List
from student.models.StudentSearchResults import StudentSearchResults
from student.models.MinimalAnswer import MinimalAnswer


class StudentSearchResultsAndAnswer(StudentSearchResults):
    search_results: List[MinimalAnswer]  # type: ignore[assignment]
