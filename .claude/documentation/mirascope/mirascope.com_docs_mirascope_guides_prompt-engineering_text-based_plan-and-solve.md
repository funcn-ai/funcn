---
url: "https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/plan-and-solve"
title: "Plan and Solve | Mirascope"
---

# Plan and Solve [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/plan-and-solve\#plan-and-solve)

[Plan and Solve](https://arxiv.org/pdf/2305.04091) is another variation of zero-shot [Chain of Thought](https://arxiv.org/abs/2201.11903) whereby the LLM is asked to reason with the improved prompt `"Q: {prompt} A: Let's first understand the problem and devise a plan to solve it. Then, let's carry out the plan and solve the problem step by step"`. Plan-and-solve has shown improvements compared to standard CoT in reasoning and mathematical tasks.

Mirascope Concepts Used

```
from mirascope.core import openai, prompt_template

pas_augment = """Let's first understand the problem and devise a plan to solve it.
Then, let's carry out the plan and solve the problem step by step."""

@openai.call(model="gpt-4o-mini")
@prompt_template("{modifiable_query}")
def call(query: str, pas_prompt: bool = False) -> openai.OpenAIDynamicConfig:
    if pas_prompt:
        modifiable_query = f"Q: {query}\nA: {pas_augment}"
    else:
        modifiable_query = query
    return {"computed_fields": {"modifiable_query": modifiable_query}}

prompt = """The school cafeteria ordered 42 red apples and 7 green apples for
students lunches. But, if only 9 students wanted fruit, how many extra did the
cafeteria end up with?"""

print(call(query=prompt, pas_prompt=True))
```

```
To find out how many extra apples the cafeteria ended up with, we can follow these steps:

1. **Calculate the total number of apples ordered:**
    - Red apples: 42
    - Green apples: 7
    - Total apples = Red apples + Green apples = 42 + 7 = 49 apples

2. **Identify how many apples were taken by the students:**
    - Number of students who wanted fruit = 9 apples (since each student is presumably taking one apple)

3. **Calculate the number of extra apples:**
    - Extra apples = Total apples - Apples taken by students
    - Extra apples = 49 - 9 = 40

Therefore, the cafeteria ended up with **40 extra apples** after the students took their fruit.
```

Effective Plan and Solve Usage

- **Encourage Structured Thinking**: The Plan and Solve approach promotes a more organized problem-solving process, starting with understanding and planning before execution.
- **Break Down Complex Problems**: Use this technique for problems that benefit from being broken down into smaller, manageable steps.
- **Improve Problem Comprehension**: By asking the LLM to first understand the problem, it can lead to better overall comprehension and more accurate solutions.
- **Enhance Step-by-Step Reasoning**: The explicit instruction to solve the problem step by step can result in clearer, more detailed explanations.
- **Apply to Various Domains**: While particularly effective for mathematical and reasoning tasks, Plan and Solve can be adapted for a wide range of problem types.

Plan and Solve enhances the standard Chain of Thought approach by explicitly structuring the problem-solving process into distinct phases: understanding, planning, and execution. This structured approach can lead to more comprehensive and accurate solutions, especially for complex problems that benefit from careful planning before execution. By encouraging the LLM to first grasp the problem and outline a strategy, Plan and Solve can result in more thoughtful and well-organized responses across various types of reasoning and mathematical tasks.

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