---
url: "https://mirascope.com/docs/mirascope/api/core/mistral/call_response_chunk"
title: "mirascope.core.mistral.call_response_chunk | Mirascope"
---

# mirascope.core.mistral.call\_response\_chunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/mistral/call_response_chunk\#mirascope-core-mistral-call-response-chunk)

This module contains the `MistralCallResponseChunk` class.

Usage

[Streams](https://mirascope.com/docs/mirascope/learn/streams#handling-streamed-responses)

## Class MistralCallResponseChunk [Link to this heading](https://mirascope.com/docs/mirascope/api/core/mistral/call_response_chunk\#mistralcallresponsechunk)

A convenience wrapper around the Mistral `ChatCompletionChunk` streamed chunks.

When calling the Mistral API using a function decorated with `mistral_call` and
`stream` set to `True`, the stream will contain `MistralResponseChunk` instances with
properties that allow for more convenient access to commonly used attributes.

Example:

```
from mirascope.core import prompt_template
from mirascope.core.mistral import mistral_call

@mistral_call("mistral-large-latest", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

stream = recommend_book("fantasy")  # response is an `MistralStream`
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)
```

**Bases:**

[BaseCallResponseChunk](https://mirascope.com/docs/mirascope/api/core/base/call_response_chunk#basecallresponsechunk)\[CompletionChunk, [FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\]

### Attributes

| Name | Type | Description |
| --- | --- | --- |
| content | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the content of the delta. |
| finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[[FinishReason](https://mirascope.com/docs/mirascope/api/core/openai/call_response_chunk#finishreason)\] | Returns the finish reasons of the response. |
| model | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the name of the response model. |
| id | [str](https://docs.python.org/3/library/stdtypes.html#str) | Returns the id of the response. |
| usage | UsageInfo \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the usage of the chat completion. |
| input\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of input tokens. |
| cached\_tokens | [int](https://docs.python.org/3/library/functions.html#int) | Returns the number of cached tokens. |
| output\_tokens | [int](https://docs.python.org/3/library/functions.html#int) \| [None](https://docs.python.org/3/library/constants.html#None) | Returns the number of output tokens. |
| cost\_metadata | [CostMetadata](https://mirascope.com/docs/mirascope/api/core/base/types#costmetadata) | Returns the cost metadata. |
| common\_finish\_reasons | [list](https://docs.python.org/3/library/stdtypes.html#list)\[types.FinishReason\] \| [None](https://docs.python.org/3/library/constants.html#None) | - |

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