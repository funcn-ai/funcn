---
url: "https://mirascope.com/docs/mirascope/guides/prompt-engineering/chaining-based/prompt-paraphrasing"
title: "Prompt Paraphrasing: Generating Diverse Prompts for LLM Testing and Evaluation | Mirascope"
---

# Prompt Paraphrasing: Generating Diverse Prompts for LLM Testing and Evaluation [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/chaining-based/prompt-paraphrasing\#prompt-paraphrasing-generating-diverse-prompts-for-llm-testing-and-evaluation)

[Prompt Paraphrasing](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00324/96460/How-Can-We-Know-What-Language-Models-Know) is not a prompt engineering technique, but rather a prompt generation technique used to create ensembles of prompts for testing or other prompt engineering techniques. In this example, we cover a specific method of generating prompts mentioned in the paper whereby a prompt is translated into $B$ versions in another language, then backtranslated into $B^2$ versions to English.

Mirascope Concepts Used

## Implementation [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/chaining-based/prompt-paraphrasing\#implementation)

Let's implement the Prompt Paraphrasing technique using Mirascope:

```
from mirascope.core import openai, prompt_template
from pydantic import BaseModel, Field

class Translations(BaseModel):
    translations: list[str] = Field(
        ..., description="The list of translations into the requested language"
    )

@openai.call(model="gpt-4o-mini", response_model=Translations)
@prompt_template(
    """
    For this phrase: {phrase}

    Give {num_translations} translations in {language}
    """
)
def translate(phrase: str, language: str, num_translations: int): ...

def prompt_paraphrasing(query: str, num_translations: int = 3) -> set[str]:
    spanish_translations = translate(
        phrase=query,
        language="Spanish",
        num_translations=num_translations,
    )
    # Avoid Duplicates
    prompt_variations = set()
    for spanish_phrase in spanish_translations.translations:
        back_translations = translate(
            spanish_phrase, language="English", num_translations=3
        )
        prompt_variations.update(back_translations.translations)
    return prompt_variations

print(
    prompt_paraphrasing(
        query="What are some manageable ways to improve my focus and productivity?"
    )
)
```

How can I enhance my concentration and increase my productivity in a sustainable manner?

This implementation consists of two main functions:

1. `translate`: This function takes a phrase, target language, and number of translations as input, and returns multiple translations of the phrase in the specified language.
2. `prompt_paraphrasing`: This function orchestrates the Prompt Paraphrasing technique. It first translates the input query into Spanish, then back-translates each Spanish translation into English, creating a set of diverse prompt variations.

## Benefits and Considerations [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/chaining-based/prompt-paraphrasing\#benefits-and-considerations)

The Prompt Paraphrasing implementation offers several advantages:

1. Generation of diverse prompt variations for more robust LLM testing and evaluation.
2. Potential discovery of more effective phrasings for specific tasks or queries.
3. Improved understanding of LLM behavior across different linguistic formulations.

When implementing this technique, consider:

- Balancing the number of translations and languages with computational cost and time constraints.
- Selecting appropriate languages for translation based on your specific use case or target audience.
- Implementing a filtering mechanism to remove nonsensical or overly divergent paraphrases.

Additional Real-World Applications

- **Robustness Testing**: Use prompt paraphrasing to test LLM performance across various phrasings of the same query.
- **Data Augmentation**: Generate additional training data by paraphrasing existing prompts or questions.
- **Chatbot Improvement**: Enhance chatbot understanding by training on paraphrased versions of common queries.
- **Cross-lingual Information Retrieval**: Improve search results by querying with multiple paraphrased versions of the search term.
- **Writing Assistance**: Offer users alternative phrasings for their writing to improve clarity or style.

When adapting this recipe to your specific use-case, consider:

- Experimenting with different source and target languages for translation.
- Implementing a scoring mechanism to rank paraphrases based on relevance or quality.
- Combining Prompt Paraphrasing with other techniques like Chain of Thought or Self-Consistency for more comprehensive LLM evaluation.
- Developing a feedback loop to refine the paraphrasing process based on LLM performance on different prompt variations.

By leveraging Mirascope calls and response models, you can easily implement and customize the Prompt Paraphrasing technique to generate diverse prompts for LLM testing, evaluation, and improvement across a wide range of applications.

Copy as Markdown

#### Provider

OpenAI

#### On this page

Copy as Markdown

#### Provider

OpenAI

#### On this page

## Cookie Consent

We use cookies to track usage and improve the site.

RejectAccept