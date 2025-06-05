---
url: "https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/role-prompting"
title: "Role Prompting | Mirascope"
---

# Role Prompting [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/role-prompting\#role-prompting)

[Role prompting](https://arxiv.org/pdf/2311.10054) is a commonly used prompt engineering technique where responses can be improved by setting the roles of the LLM or the audience within the conversation. The paper linked above showcases some analytics for which roles perform best for specific tasks. Role prompting can improve response quality in both accuracy based and open ended tasks.

Mirascope Concepts Used

```
from mirascope.core import openai, prompt_template

@openai.call(model="gpt-4o-mini")
@prompt_template("""
    SYSTEM: {llm_role} {audience}
    USER: {query}
    """)
def call(
    query: str, llm_role: str | None = None, audience: str | None = None
) -> openai.OpenAIDynamicConfig:
    return {
        "computed_fields": {
            "llm_role": f"You are {llm_role}." if llm_role else "",
            "audience": f"You are talking to {audience}." if audience else "",
        }
    }

response = call(
    query="What's the square root of x^2 + 2x + 1?",
    llm_role="a math teacher",
    audience="your student",
)
print(response.content)
```

```
To find the square root of the expression \( x^2 + 2x + 1 \), we can first recognize that this expression can be factored.

The expression \( x^2 + 2x + 1 \) is a perfect square trinomial, and it can be factored as:

\[\
(x + 1)^2\
\]

Now, we can take the square root of this expression:

\[\
\sqrt{x^2 + 2x + 1} = \sqrt{(x + 1)^2}\
\]

Taking the square root of a square gives us the absolute value:

\[\
\sqrt{(x + 1)^2} = |x + 1|\
\]

So, the final result is:

\[\
\sqrt{x^2 + 2x + 1} = |x + 1|\
\]
```

In this example, we're using role prompting to set the LLM's role as a math teacher and the audience as a student. This context can help the LLM tailor its response to be more educational and easier to understand, as a teacher would explain to a student.

## Benefits of Role Prompting [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/role-prompting\#benefits-of-role-prompting)

1. **Contextual Responses**: By setting roles, the LLM can provide responses that are more appropriate for the given context.
2. **Improved Accuracy**: For certain tasks, setting the right role can lead to more accurate or relevant information.
3. **Tailored Language**: The LLM can adjust its language and explanation style based on the roles, making responses more suitable for the intended audience.
4. **Enhanced Creativity**: For open-ended tasks, role prompting can lead to more diverse and creative responses.

Effective Role Prompting

- **Choose Relevant Roles**: Select roles that are appropriate for the task or query at hand.
- **Be Specific**: The more specific you are about the roles, the better the LLM can tailor its response.
- **Experiment**: Try different role combinations to see which produces the best results for your specific use case.
- **Consider the Audience**: Setting an audience role can be just as important as setting the LLM's role.
- **Combine with Other Techniques**: Role prompting can be used in conjunction with other prompt engineering techniques for even better results.

By leveraging role prompting, you can guide the LLM to provide responses that are more aligned with your specific needs and context.

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