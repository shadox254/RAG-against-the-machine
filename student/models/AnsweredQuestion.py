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
#  File: AnsweredQuestion.py                                                  #
#  By: rruiz <rruiz@student.42.fr>                                            #
#  Created: 2026/06/16 10:21:50 by rruiz                                      #
#  Updated: 2026/06/16 11:44:36 by rruiz                                      #
# *************************************************************************** #

from typing import List
from student.models.MinimalSource import MinimalSource
from student.models.UnansweredQuestion import UnansweredQuestion


class AnsweredQuestion(UnansweredQuestion):
    sources: List[MinimalSource]
    answer: str
