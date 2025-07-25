---
url: "https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/common-phrases"
title: "Common Phrases (Prompt Mining) | Mirascope"
---

# Common Phrases (Prompt Mining) [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/common-phrases\#common-phrases-prompt-mining)

Sometimes, an LLM can appear to know more or less about a topic depending on the phrasing you use because a specific bit of information shows up far more frequently in its training data with a specific phrasing. Prompt Mining, explained in [this paper](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00324/96460/How-Can-We-Know-What-Language-Models-Know), involves various methods of searching for the phrase which gives the best response regarding a topic.

Mirascope Concepts Used

Prompt Mining itself is an extensive endeavor, but the takeaway is that LLMs are likely to give better answers when the question uses phrases that the LLM has been trained on. Here is an example where using common jargon regarding a video game produces a real answer, and a generic prompt doesn’t:

```
from mirascope.core import openai

@openai.call(model="gpt-4o-mini")
def call(query: str):
    return query

generic_response = call(
    """Does the roy in smash bros ultimate have a reliable way to knock out an\
        opponent that starts with the A button?"""
)
engineered_response = call(
    """In smash bros ultimate, what moves comprise Roy's kill confirm combo that\
        starts with jab?"""
)

print(generic_response)
print(engineered_response)
```

Yes, in Super Smash Bros. Ultimate, Roy has a reliable way to knock out an opponent using an attack that starts with the A button. His forward tilt (dtilt), also known as the "F tilt," is a strong move that can lead to knockouts if used correctly, especially at higher percentages. Additionally, his neutral attack (AAA combo) can set up for follow-up attacks or build damage, although it's not typically a kill move on its own.

If you are looking specifically for a move that can knock out and starts with the A button, Roy's forward aerial (aerial attack) is also a strong option, particularly towards the edge of the stage when opponents are at higher percentages.

Keep in mind that spacing and timing are key to landing these moves effectively!
In Super Smash Bros. Ultimate, Roy's jab kill confirm combo typically involves starting with his jab, specifically the rapid jabs. After hitting the opponent with the jab, players can follow up with:

1. **Jab (rapid jabs)** \- Connects with the first few hits.
2. **F-tilt (Forward Tilt)** \- After the jab, quickly input F-tilt to catch the opponent off-guard. The jab pushes the opponent slightly away, and if done correctly, the F-tilt can connect reliably.

The timing and spacing are crucial for this combo to work effectively, and it often relies on the opponent being at a higher percentage for the F-tilt to secure the KO. Additionally, if performed correctly, this can work as an effective kill confirm at kill percentages.

As you can see, using common phrases and jargon specific to the topic (in this case, Super Smash Bros. Ultimate) can lead to more accurate and detailed responses from the LLM. This technique can be particularly useful when dealing with specialized or technical subjects.

## Tips for Using Common Phrases [Link to this heading](https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/common-phrases\#tips-for-using-common-phrases)

1. **Research the topic**: Familiarize yourself with the common terminology and phrases used in the field you're querying about.

2. **Use specific jargon**: Incorporate field-specific terms that are likely to appear in the LLM's training data.

3. **Experiment with different phrasings**: Try multiple versions of your query using different common phrases to see which yields the best results.

4. **Be aware of potential biases**: Remember that using common phrases might reinforce existing biases in the training data.

5. **Combine with other techniques**: Use this approach in conjunction with other prompt engineering techniques for even better results.


By leveraging common phrases and domain-specific language, you can often elicit more accurate and detailed responses from LLMs, especially when dealing with specialized topics or technical subjects.

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