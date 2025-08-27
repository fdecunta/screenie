# screenie

<p align="center">
  <img src="/docs/screenie.png" alt="Project Logo" width="200"/>
</p>

**Work in progress, early stage!**

A command-line tool to help researchers screen papers for systematic reviews using LLM APIs and experiment with different configurations.

## How it works

1. **Import** papers from bibliography files (BibTeX, RIS)
2. **Configure** your LLM model and API keys
3. **Create a Recipe** defining model, prompt, and criteria for reproducible experiments
4. **Run** screening - the LLM evaluates studies using the instructions in the recipe
5. **Export** results with LLM recommendations (include or exclude) and explanations

## Recipes

Recipes are TOML files that define screening instructions. They allow you to easily experiment with different models, model configurations, prompts, and criteria.

The prompt section uses placeholders that are automatically filled with your criteria and each paper's information:

```toml
[model]
model = "openai/gpt-4o"
temperature = 0
max_tokens = 1500

[criteria]
text = """
1. Include studies that test LLM performance in systematic reviews
2. Include only peer-reviewed articles published after 2020
3. ...
"""

[prompt]
text = """
You are assisting with systematic review screening.
Evaluate this study against the inclusion criteria.

Criteria: $criteria

Study:
Title: $title
Authors: $authors  
Year: $year
Abstract: $abstract
"""
```

## Quick Start

```bash
# Store your API keys
screenie config

# Initialize a new project
screenie init my-review

# Import papers
screenie import --from papers.bib --to my-review.db

# Create a recipe file (my-recipe.toml)
# Then screen 10 studies
screenie run my-recipe.toml my-review.db --limit 10

# Export results
screenie export my-review.db --format csv
```

## Installation (Development)

This is early-stage software not yet available on PyPI. To install the development version:

```bash
# Clone the repository
git clone https://github.com/your-username/screenie.git
cd screenie

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

