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
#  File: RagDataset.py                                                        #
#  By: rruiz <rruiz@student.42.fr>                                            #
#  Created: 2026/06/16 10:22:42 by rruiz                                      #
#  Updated: 2026/06/16 11:44:37 by rruiz                                      #
# *************************************************************************** #

from pydantic import BaseModel
from typing import List
from student.models.AnsweredQuestion import AnsweredQuestion
from student.models.UnansweredQuestion import UnansweredQuestion


class RagDataset(BaseModel):
    rag_questions: List[AnsweredQuestion | UnansweredQuestion]
