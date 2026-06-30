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

MYPY_FLAGS		= --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
UV_VERSION		= uv --version
UV_INSTALL		= curl -LsSf https://astral.sh/uv/install.sh | sh
SRC				= student
MAX_CHUNK_SIZE	=
QUESTION		=
K				=
DATASET_PATH	=
SAVE_DIRECTORY	=

install:
	@if ! $(UV_VERSION) > /dev/null 2>&1; then\
		$(UV_INSTALL); \
	fi
	@uv sync

run: install
	clear
	@uv run python -m $(SRC)

index: install
	clear
	uv run python -m $(SRC) index --max_chunk_size $(MAX_CHUNK_SIZE)

search: install
	clear
	uv run python -m $(SRC) search "$(QUESTION)" --k $(K)

search_dataset: install
	clear
	uv run python -m $(SRC) search_dataset --dataset_path "$(DATASET_PATH)" --k $(K) --save_directory $(SAVE_DIRECTORY)

answer: install

answer_dataset: install

evaluate: install

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

.PHONY: install run debug clean fclean lint lint-strict
.SILENT: