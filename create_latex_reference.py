# -*- coding: utf-8 -*-
"""Generate the markdown file with a reference based on the
macros from get_jupyterbook_latex_macros.py
"""
# @Author: Aaron Reding
# @Date:   2023-07-15 02:18:14
# @Last Modified by:   aaronreding
# @Last Modified time: 2023-07-15 22:36:11
import os
import openai
from openai.openai_object import OpenAIObject
from datetime import datetime


def load_api_key() -> str:
    """Load API key from current environment or throw KeyError

    Returns:
        str: openai api key
    """
    try:
        return os.environ["CHATGPT_KEY"]
    except KeyError:
        print("API_KEY not found")
        return ""


def load_macros() -> str:
    """Return a str of the file generated by get_jupyterbook_latex_macros.py

    Returns:
        str: file output from get_jupyterbook_latex_macros.py
    """
    with open("macros_used.txt", "r") as f:
        macros = f.read()

    return macros


def get_completions_response(base_prompt: str, text: str, model: str) -> OpenAIObject:
    """This is the outdated completions API for GPT-3. Don't recommend.

    Args:
        base_prompt (str): describe context of question and set up the model
        text (str): put the macros here
        model (str): completions model name (e.g. text-davinci-003)

    Returns:
        OpenAIObject: response object
    """
    response = openai.Completion.create(
        model=model,
        prompt=base_prompt + text,
        temperature=1,
        max_tokens=4000,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=1,
    )

    return response


def get_chat_response(base_prompt: str, text: str, model: str) -> OpenAIObject:
    """New chat completion API. Better in every way (even cheaper if using GPT 3.5)

    Args:
        base_prompt (str): describe context of question and set up the model
        text (str): put the macros here
        model (str): chat model name (e.g. gpt-4)

    Returns:
        OpenAIObject: response object
    """
    text_plus = f"""
    The following are latex macros commonly used in a Bayesian statistics class:
    {text}
    """

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": base_prompt},
            {"role": "user", "content": text_plus},
        ],
        temperature=0.5,
    )

    return response


def write_file(response: str, model_type: str):
    """Save the generated markdown file.

    Args:
        response (str): Description
        model_type (str): Description
        macros (set)
    """
    current_time = datetime.now()
    time_string = current_time.strftime("%Y-%m-%d_%H-%M")
    filename = f"latex_reference_{model_type}_{time_string}.md"
    print(f"Writing {filename}")

    with open(filename, "w") as f:
        f.write(response)


def main():
    key = load_api_key()
    openai.api_key = key
    macros = load_macros()

    base_prompt = """
        You are a technical writer specializing in LATEX reference documents. Your
        users give you lists containing only latex macro names.

        Your job is to organize them into categories (an example
        category that should be included is "Greek Letters") and add a brief example,
        then return them in a Markdown document of the following format:

        # Latex Reference
        ## Category
        macro name, $\\macro$, brief description of macro with basic example.
        ## Category
        ...

        You also add other relevent macros. For example, in the Greek Letters
        category, you should include the full Greek alphabet, keeping capital and
        lowercase letters together. But in other categories,
        you should be very very selective about what you add so that the reference
        document isn't too long and hard to read.
    """
    # Old GPT3 completions API
    # model = "text-davinci-003"
    # response = get_completions_response(key, base_prompt, macros, model)
    # response_text = response["choices"][0]["text"]

    # GPT 3.5 or GPT 4
    # model = "gpt-3.5-turbo"
    model = "gpt-4"
    # model = "gpt-4-32k" not currently available over API
    response = get_chat_response(base_prompt, macros, model)
    response_text = response["choices"][0]["message"]["content"]

    write_file(response_text, model_type=model)


if __name__ == "__main__":
    main()
