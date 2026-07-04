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
#  File: answering.py                                                         #
#  By: rruiz <rruiz@student.42.fr>                                            #
#  Created: 2026/06/30 10:02:19 by rruiz                                      #
#  Updated: 2026/07/04 16:08:49 by rruiz                                      #
# *************************************************************************** #

from student.search.retriever import search, load_indexes
from student.models.MinimalSource import MinimalSource
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Any
import torch


def answerer(query: str, k: int) -> None:
    """
    Searches for relevant sources for a given query, compiles the context,
    generates an answer using the model, and prints it to the console.

    Args:
        query (str): The user's question to be answered.
        k (int): The number of relevant sources to retrieve for the context.
    """

    indexes = load_indexes()

    research = search(query, k, indexes)

    context = ''
    for source in research.retrieved_sources:
        context += f'{get_content(source)}\n'

    model_name = "Qwen/Qwen3-0.6B"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model: Any = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto"
    )

    response = answering(context, query, tokenizer, model)
    print(response)


def answering(
        context: str,
        query: str,
        tokenizer: Any,
        model: Any
        ) -> str:
    """
    Generates an answer to a question using the Qwen/Qwen3-0.6B model based
    strictly on the provided context.

    Args:
        user_txt (str): The compiled context text from retrieved sources.
        query (str): The question asked by the user.

    Returns:
        str: The generated text response, cleaned of special tokens.
    """

    system_txt = """Answer the question using ONLY the context provided with
     this information; do not make anything up—everything must come from the
     context. If you don't know the answer, simply reply, "I don't know."
     Keep your answer short and direct: at most 2-3 sentences, with no
     repetition of the question or the context."""

    messages = [
        {"role": "system", "content": system_txt},
        {
            "role": "user",
            "content": (
                f"Context:\n{context}\n\n"
                f"Question: {query}\n\n"
                "Answer the question above using only the context provided."
                ),
                },
            ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=60
    )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

    try:
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0

    decoded_output = tokenizer.decode(
        output_ids[index:],
        skip_special_tokens=True
        )

    response = str(decoded_output).strip("\n")
    torch.cuda.empty_cache()

    return response


def get_content(response: MinimalSource) -> str:
    """
    Extracts the exact text slice from a source file using the character
    indices defined in the response object.

    Args:
        response (MinimalSource): Object containing source metadata.
        i (int): The index or number of the source.

    Returns:
        str: A formatted string containing the file name and the extracted
            text slice.
    """

    file = response.file_path
    first_c_idx = response.first_character_index
    last_c_idx = response.last_character_index

    with open(file, 'r') as f:
        text = f.read()

    return f'[{file}]\n {text[first_c_idx:last_c_idx]}\n'
