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
#  Updated: 2026/06/16 10:29:12 by rruiz                                      #
# *************************************************************************** #

from typing import List
from src.models.MinimalSource import MinimalSource
from src.models.UnansweredQuestion import UnansweredQuestion


class AnsweredQuestion(UnansweredQuestion):
    sources: List[MinimalSource]
    answer: str
