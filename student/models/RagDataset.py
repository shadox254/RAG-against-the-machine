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
#  Updated: 2026/06/16 10:29:33 by rruiz                                      #
# *************************************************************************** #

from pydantic import BaseModel
from typing import List
from src.models.AnsweredQuestion import AnsweredQuestion
from src.models.UnansweredQuestion import UnansweredQuestion


class RagDataset(BaseModel):
    rag_questions: List[AnsweredQuestion | UnansweredQuestion]
