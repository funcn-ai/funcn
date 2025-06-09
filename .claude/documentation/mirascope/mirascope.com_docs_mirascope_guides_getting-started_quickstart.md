---
url: "https://mirascope.com/docs/mirascope/guides/getting-started/quickstart"
title: "Quickstart | Mirascope"
---

# Quickstart [Link to this heading](https://mirascope.com/docs/mirascope/guides/getting-started/quickstart\#quickstart)

Mirascope supports various LLM providers, including [OpenAI](https://openai.com/), [Anthropic](https://www.anthropic.com/), [Mistral](https://mistral.ai/), [Gemini](https://gemini.google.com/), [Groq](https://groq.com/), [Cohere](https://cohere.com/), [LiteLLM](https://www.litellm.ai/), [Azure AI](https://azure.microsoft.com/en-us/solutions/ai), and [Vertex AI](https://cloud.google.com/vertex-ai). You can select your preferred provider using the dropdown menu in the sidebar to the right. (Just below 'Copy as Markdown'!)

## Setup [Link to this heading](https://mirascope.com/docs/mirascope/guides/getting-started/quickstart\#setup)

Let's start by installing Mirascope and setting up your API keys:

MacOS / LinuxWindows

```
pip install "mirascope[openai]"
export OPENAI_API_KEY=XXXX
```

This installs Mirascope with the necessary packages for your chosen provider and configures the appropriate API keys.

## Basic LLM Call [Link to this heading](https://mirascope.com/docs/mirascope/guides/getting-started/quickstart\#basic-llm-call)

The `call` decorator in Mirascope transforms Python functions into LLM API calls. This allows you to seamlessly integrate LLM interactions into your Python code.

```
from mirascope import llm

@llm.call(provider="openai", model="gpt-4o-mini")
def get_capital(country: str) -> str:
    return f"What is the capital of {country}?"

response = get_capital("Japan")
print(response.content)
```

```
The capital of Japan is Tokyo.
```

In this example:

1. We import the `llm` module from Mirascope, which provides the `call` decorator.
2. The `@llm.call` decorator specifies which provider and model to use.
3. We return the content of a single user message in the function body.
4. When we call `get_capital("Japan")`, it templates the prompt, sends a request to the provider's API, and returns the response.
5. We print the `content` of the response, which contains the LLM's answer.

This approach allows you to use LLMs as if they were regular Python functions, making it easy to integrate AI capabilities into your applications.

## Streaming Responses [Link to this heading](https://mirascope.com/docs/mirascope/guides/getting-started/quickstart\#streaming-responses)

Streaming allows you to process LLM responses in real-time, which is particularly useful for long-form content generation or when you want to provide immediate feedback to users.

```
from mirascope import llm

@llm.call(provider="openai", model="gpt-4o-mini", stream=True)
def stream_city_info(city: str) -> str:
    return f"Provide a brief description of {city}."

for chunk, _ in stream_city_info("Tokyo"):
    print(chunk.content, end="", flush=True)
```

```
Tokyo, the capital of Japan, is a vibrant metropolis known for its unique blend of tradition and modernity. As one of the world's most populous cities, it features a bustling urban landscape filled with skyscrapers, renowned shopping districts like Shibuya and Ginza, and cultural landmarks such as the historic Senso-ji Temple. Tokyo is also famous for its diverse culinary scene, ranging from street food to Michelin-starred restaurants. The city's efficient public transportation system makes it easy to explore its many neighborhoods, each offering distinct experiences, whether it's the tranquil gardens of Ueno, the electronic town of Akihabara, or the fashion-forward streets of Harajuku. With its rich cultural heritage, cutting-edge technology, and constant innovation, Tokyo embodies the essence of contemporary urban life.
```

Here's what's happening in this streaming example:

1. We use the `stream=True` parameter in the `@llm.call` decorator to enable streaming.
2. The function returns an iterator that yields chunks of the response as they become available.
3. We iterate over the chunks, printing each one immediately.
4. The `end=""` and `flush=True` parameters in the print function ensure that the output is displayed in real-time without line breaks.

Streaming is beneficial for:

- Providing immediate feedback to users
- Processing very long responses efficiently
- Implementing typewriter-like effects in user interfaces

## Response Models [Link to this heading](https://mirascope.com/docs/mirascope/guides/getting-started/quickstart\#response-models)

Response models in Mirascope allow you to structure and validate the output from LLMs. This feature is particularly useful when you need to ensure that the LLM's response adheres to a specific format or contains certain fields.

```
from mirascope import llm
from pydantic import BaseModel

class Capital(BaseModel):
    city: str
    country: str

@llm.call(provider="openai", model="gpt-4o-mini", response_model=Capital)
def extract_capital(query: str) -> str:
    return f"{query}"

capital = extract_capital("The capital of France is Paris")
print(capital)
```

```
city='Paris' country='France'
```

## JSON Mode [Link to this heading](https://mirascope.com/docs/mirascope/guides/getting-started/quickstart\#json-mode)

JSON mode allows you to directly parse LLM outputs as JSON. This is particularly useful when you need structured data from your LLM calls.

```
from mirascope import llm

@llm.call(provider="openai", model="gpt-4o-mini", json_mode=True)
def city_info(city: str) -> str:
    return f"Provide information about {city} in JSON format"

response = city_info("Tokyo")
print(response.content)  # This will be a JSON-formatted string
```

```
{
  "city": "Tokyo",
  "country": "Japan",
  "population": 13929286,
  "area_km2": 2191,
  "language": ["Japanese"],
  "currency": {
    "name": "Yen",
    "symbol": "¥"
  },
  "landmarks": [\
    {\
      "name": "Tokyo Tower",\
      "type": "Observation Tower"\
    },\
    {\
      "name": "Shibuya Crossing",\
      "type": "Famous Intersection"\
    },\
    {\
      "name": "Senso-ji Temple",\
      "type": "Historic Site"\
    },\
    {\
      "name": "Meiji Shrine",\
      "type": "Shinto Shrine"\
    }\
  ],
  "transportation": {
    "rail": {
      "types": ["Subway", "Light Rail", "High-Speed Rail"],
      "notable_lines": ["Yamanote Line", "Chuo Line", "Tozai Line"]
    },
    "airport": ["Narita International Airport", "Haneda Airport"]
  },
  "cuisine": [\
    "Sushi",\
    "Ramen",\
    "Tempura",\
    "Yakitori"\
  ],
  "climate": {
    "type": "Humid subtropical",
    "average_temperature": {
      "summer": "26°C",
      "winter": "5°C"
    },
    "average_precipitation_mm": 1650
  }
}
```

JSON mode is beneficial for:

- Ensuring structured outputs from LLMs
- Easy integration with data processing pipelines
- Creating APIs that return JSON data

Note that not all providers have an explicit JSON mode. For those providers, we attempt to instruct the model to provide JSON; however, there is no guarantee that it will output only JSON.

You can combine `json_mode=True` with `response_model` to automatically parse the JSON output into a Pydantic model:

```
from mirascope import llm
from pydantic import BaseModel

class CityInfo(BaseModel):
    name: str
    population: int
    country: str

@llm.call(provider="openai", model="gpt-4o-mini", json_mode=True, response_model=CityInfo)
def city_info(city: str) -> str:
    return f"Provide information about {city} in JSON format"

response = city_info("Tokyo")
print(
    f"Name: {response.name}, Population: {response.population}, Country: {response.country}"
)
```

```
Name: Tokyo, Population: 13929286, Country: Japan
```

## Asynchronous Processing [Link to this heading](https://mirascope.com/docs/mirascope/guides/getting-started/quickstart\#asynchronous-processing)

Mirascope supports asynchronous processing, allowing for efficient parallel execution of multiple LLM calls. This is particularly useful when you need to make many LLM calls concurrently or when working with asynchronous web frameworks.

```
from mirascope import llm
import asyncio
from pydantic import BaseModel

class Capital(BaseModel):
    city: str
    country: str

@llm.call(provider="openai", model="gpt-4o-mini", response_model=Capital)
async def get_capital_async(country: str) -> str:
    return f"What is the capital of {country}?"

async def main():
    countries = ["France", "Japan", "Brazil"]
    tasks = [get_capital_async(country) for country in countries]
    capitals = await asyncio.gather(*tasks)
    for capital in capitals:
        print(f"The capital of {capital.country} is {capital.city}")

# For a Python script, uncomment this line:
# asyncio.run(main())

# For demonstration purposes only (this won't work in a regular Python script):
# In a Jupyter notebook or interactive environment you would use:
# await main()
```

```
The capital of France is Paris
The capital of Japan is Tokyo
The capital of Brazil is Brasília
```

This asynchronous example demonstrates:

1. An async version of our `get_capital` function, defined with `async def`.
2. Use of `asyncio.gather()` to run multiple async tasks concurrently.
3. Processing of results as they become available.

Asynchronous processing offers several advantages:

- Improved performance when making multiple LLM calls
- Better resource utilization
- Compatibility with async web frameworks like FastAPI or aiohttp

## Output Parsers [Link to this heading](https://mirascope.com/docs/mirascope/guides/getting-started/quickstart\#output-parsers)

Output parsers allow you to process LLM responses in custom formats. These enable a lot of different ways to structure and
extract from LLM outputs; for example using regular expressions to extract from xml tags.

```
import re

from mirascope import llm, prompt_template

def parse_cot(response: llm.CallResponse) -> str:
    pattern = r"<thinking>.*?</thinking>.*?<output>(.*?)</output>"
    match = re.search(pattern, response.content, re.DOTALL)
    if not match:
        return response.content
    return match.group(1).strip()

@llm.call(provider="openai", model="gpt-4o-mini", output_parser=parse_cot)
@prompt_template(
    """
    First, output your thought process in <thinking> tags.
    Then, provide your final output in <output> tags.

    Question: {question}
    """
)
def chain_of_thought(question: str):
    pass

question = "Roger has 5 tennis balls. He buys 2 cans of 3. How many does he have now?"
output = chain_of_thought(question)
print(output)
```

In this example, we ask the model to produce a chain of thought as well as a final output,
and the output parser separates these two pieces in a convenient fashion.

Output parsers are useful for:

- Extracting specific formats or data structures from LLM responses
- Cleaning and standardizing LLM outputs
- Implementing custom post-processing logic

## Next Steps [Link to this heading](https://mirascope.com/docs/mirascope/guides/getting-started/quickstart\#next-steps)

This concludes our Quickstart Guide to Mirascope. We've covered the main features of the library, including prompt templates, basic calls, streaming, response models, asynchronous processing, JSON mode, and output parsers. Each of these features can be combined and customized to create powerful, flexible AI applications.

If you like what you've seen so far, [give us a star](https://github.com/Mirascope/mirascope) and [join our community](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA).

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