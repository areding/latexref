# Auto-generated Latex reference for Jupyter Books

Scripts to scan a [Jupyter Book](https://jupyterbook.org/en/stable/intro.html) for all Latex macros used and generate a reference file using the [OpenAI API](https://platform.openai.com/docs/api-reference/introduction).

## Usage

First adjust the folder structure and path and run ```get_jupyterbook_latex_macros.py``` to get the macros in the Jupyter Book.

Then run ```create_latex_reference.py``` to create the markdown file through OpenAI's API. Make sure you set your OpenAI key to ```CHATGPT_KEY``` in your environment or edit the ```load_api_key()```function.

## Limitations

Right now it's very basic. After I used it the first time, it turned out the [book](https://areding.github.io/6420-pymc/intro.html) I made it for didn't as many different Latex commands as I thought. If I need it again in the future I might fix some of these.

- Right now it only detects macros like ```\alpha``` or ```\ge```. Would like to capture commands like \begin{align*} as well.
- The folder structure is specific to my Jupyter book. Will need to generalize if used on other projects.
- It only returns markdown or ipynb files.
- Logic for getting the macros using [pylatexenc](https://pylatexenc.readthedocs.io/en/latest/latexwalker) could be improved. Right now relying on a cleaning function afterwards, but that's only feasible because there are only ~50 results in my book.
- Might be nice to have a template markdown file and have GPT generate a JSON or YAML for it instead.
- Relies on GPT for organization so it's inconsistent sometimes but pretty good. Could experiment with temperature and other settings.

