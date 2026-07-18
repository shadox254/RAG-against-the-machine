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
#  File: Makefile                                                             #
#  By: rruiz <rruiz@student.42.fr>                                            #
#  Created: 2026/06/15 15:13:42 by rruiz                                      #
#  Updated: 2026/07/17 11:15:13 by rruiz                                      #
# *************************************************************************** #

MYPY_FLAGS					= --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
UV_VERSION					= uv --version
UV_INSTALL					= curl -LsSf https://astral.sh/uv/install.sh | sh
SRC							= student


install:
	@if ! $(UV_VERSION) > /dev/null 2>&1; then\
		$(UV_INSTALL); \
	fi
	@uv sync

run: install
	@uv run python -m $(SRC)

index: install
	uv run python -m student index --max_chunk_size 2000

search: install
	uv run python -m student search "How to configure OpenAI server?" --k 10

search_dataset: install
	uv run python -m student search_dataset --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json --k 10 --save_directory data/output/search_results
	uv run python -m student search_dataset --dataset_path data/datasets/UnansweredQuestions/dataset_code_public.json --k 10 --save_directory data/output/search_results

answer: install
	uv run python -m student answer "How to configure OpenAI server?" --k 10

answer_dataset: install
	uv run python -m student answer_dataset --student_search_results_path data/output/search_results/dataset_docs_public.json --save_directory data/output/search_results_and_answer
	uv run python -m student answer_dataset --student_search_results_path data/output/search_results/dataset_code_public.json --save_directory data/output/search_results_and_answer

evaluate: install
	echo 'Evaluate docs'
	uv run python -m student evaluate --student_answer_path data/output/search_results/dataset_docs_public.json --dataset_path data/datasets/AnsweredQuestions/dataset_docs_public.json --k 10
	echo 'Evaluate code'
	uv run python -m student evaluate --student_answer_path data/output/search_results/dataset_code_public.json --dataset_path data/datasets/AnsweredQuestions/dataset_code_public.json --k 10

debug:
	@uv run python -m pdb -m $(SRC)

clean:
	@rm -rf .mypy_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean
	@rm -rf .venv
	@rm -rf data/processed
	@rm -rf data/output
	@rm -rf hf_cache

lint:
	@-uv run flake8 $(SRC)
	@-uv run mypy $(SRC) $(MYPY_FLAGS)

lint-strict:
	@-uv run flake8 $(SRC)
	@-uv run mypy $(SRC) $(MYPY_FLAGS) --strict

.PHONY: install run index search search_dataset answer answer_dataset evaluate debug clean fclean lint lint-strict
.SILENT:
