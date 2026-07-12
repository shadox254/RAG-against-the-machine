# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  Makefile                                          :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: alebaron, rruiz                           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/05/18 16:14:58 by alebaron        #+#    #+#               #
#  Updated: 2026/05/20 09:46:09 by rruiz           ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

MYPY_FLAGS					= --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
UV_VERSION					= uv --version
UV_INSTALL					= curl -LsSf https://astral.sh/uv/install.sh | sh
SRC							= student
MAX_CHUNK_SIZE				=
QUESTION					=
K							=
DATASET_PATH				=
SAVE_DIRECTORY				=
MODEL_NAME					= Qwen/Qwen3-0.6B
MAX_CONTEXT_LENGTH			= 2000
STUDENT_SEARCH_RESULTS_PATH	=
STUDENT_ANSWER_PATH			=


install:
	@if ! $(UV_VERSION) > /dev/null 2>&1; then\
		$(UV_INSTALL); \
	fi
	@uv sync

run: install
	@uv run python -m $(SRC)

index: install
	uv run python -m $(SRC) index --max_chunk_size $(MAX_CHUNK_SIZE)

search: install
	uv run python -m $(SRC) search "$(QUESTION)" --k $(K)

search_dataset: install
	clear
	uv run python -m $(SRC) search_dataset --dataset_path "$(DATASET_PATH)" --k $(K) --save_directory $(SAVE_DIRECTORY)

answer: install
	uv run python -m $(SRC) answer "$(QUESTION)" --k $(K) --model_name $(MODEL_NAME) --max_context_length $(MAX_CONTEXT_LENGTH)

answer_dataset: install
	uv run python -m $(SRC) answer_dataset --student_search_results_path "$(STUDENT_SEARCH_RESULTS_PATH)" --save_directory $(SAVE_DIRECTORY) --k $(K) --max_context_length $(MAX_CONTEXT_LENGTH) --model_name $(MODEL_NAME)

evaluate: install
	uv run python -m $(SRC) evaluate "$(STUDENT_ANSWER_PATH)" "$(DATASET_PATH)" --k $(K) --max_context_length $(MAX_CONTEXT_LENGTH)

debug:
	@uv run python -m pdb -m $(SRC)

clean:
	@rm -rf .mypy_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean
	@rm -rf .venv

lint:
	@-uv run flake8 $(SRC)
	@-uv run mypy $(SRC) $(MYPY_FLAGS)

lint-strict:
	@-uv run flake8 $(SRC)
	@-uv run mypy $(SRC) $(MYPY_FLAGS) --strict

.PHONY: install run index search search_dataset answer answer_dataset evaluate debug clean fclean lint lint-strict
.SILENT:
