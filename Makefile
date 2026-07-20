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
#  Updated: 2026/07/20 12:39:48 by rruiz                                      #
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
	cd student && uv run python -m src index --max_chunk_size 2000

search: install
	cd student && uv run python -m src search "How to configure OpenAI server?" --k 10

search_dataset: install
	cd student && uv run python -m src search_dataset --dataset_path ../data/datasets/UnansweredQuestions/dataset_docs_public.json --k 10 --save_directory ../data/output/search_results
	cd student && uv run python -m src search_dataset --dataset_path ../data/datasets/UnansweredQuestions/dataset_code_public.json --k 10 --save_directory ../data/output/search_results

answer: install
	cd student && uv run python -m src answer "How to configure OpenAI server?" --k 10

answer_dataset: install
	cd student && uv run python -m src answer_dataset --student_search_results_path data/output/search_results/dataset_docs_public.json --save_directory data/output/search_results_and_answer
	cd student && uv run python -m src answer_dataset --student_search_results_path data/output/search_results/dataset_code_public.json --save_directory data/output/search_results_and_answer

evaluate: install
	echo 'Evaluate docs'
	cd student && uv run python -m src evaluate --student_answer_path data/output/search_results/dataset_docs_public.json --dataset_path data/datasets/AnsweredQuestions/dataset_docs_public.json --k 10
	echo 'Evaluate code'
	cd student && uv run python -m src evaluate --student_answer_path data/output/search_results/dataset_code_public.json --dataset_path data/datasets/AnsweredQuestions/dataset_code_public.json --k 10

debug:
	@uv run python -m pdb -m $(SRC)

clean:
	@rm -rf .mypy_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean
	@rm -rf .venv
	@rm -rf data/processed
	@rm -rf data/output
	@find . -type d -name "hf_cache" -exec rm -rf {} +

lint:
	@-uv run flake8 $(SRC)
	@-uv run mypy $(SRC) $(MYPY_FLAGS)

lint-strict:
	@-uv run flake8 $(SRC)
	@-uv run mypy $(SRC) $(MYPY_FLAGS) --strict

.PHONY: install run index search search_dataset answer answer_dataset evaluate debug clean fclean lint lint-strict
.SILENT:
