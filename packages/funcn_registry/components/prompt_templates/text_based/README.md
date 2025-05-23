# Text-Based Prompt Templates

Text-based prompts are the foundation of prompt engineering. These templates demonstrate fundamental techniques for single LLM calls with various prompting strategies.

## Templates Overview

### 1. Zero-Shot Prompting (`zero_shot.py`)

Direct task execution without providing examples.

**When to use:**

- Simple, well-defined tasks
- When the model likely has sufficient knowledge
- Quick prototyping and experimentation

**Key features:**

- Minimal prompt setup
- Direct instruction format
- No examples needed

**Example use cases:**

- Basic translations
- Simple Q&A
- Format conversions

### 2. Few-Shot Learning (`few_shot.py`)

Learning from provided examples to guide output format and style.

**When to use:**

- Tasks requiring specific output format
- Domain-specific terminology or style
- Consistent pattern matching

**Key features:**

- Example-driven learning
- Format consistency
- Pattern recognition

**Example use cases:**

- Custom data formatting
- Style-specific writing
- Domain-specific classifications

### 3. Role-Based Prompting (`role_based.py`)

Assigning specific personas or expertise to the model.

**When to use:**

- Tasks requiring specialized knowledge
- Creative writing with specific voice
- Professional advice or analysis

**Key features:**

- Persona assignment
- Expertise simulation
- Perspective-based responses

**Example use cases:**

- Technical documentation (as technical writer)
- Medical advice (as doctor)
- Legal analysis (as lawyer)

### 4. Chain-of-Thought (`chain_of_thought.py`)

Step-by-step reasoning for complex problems.

**When to use:**

- Mathematical problems
- Logical puzzles
- Multi-step reasoning tasks
- Complex analysis

**Key features:**

- Explicit reasoning steps
- Intermediate work shown
- Logical progression

**Example use cases:**

- Math word problems
- Code debugging
- Strategic planning

### 5. Structured Output (`structured_output.py`)

Generating validated, type-safe outputs using Pydantic models.

**When to use:**

- API responses
- Data extraction
- Form generation
- Integration with type systems

**Key features:**

- Pydantic model validation
- Type safety
- Consistent structure
- JSON serialization

**Example use cases:**

- Contact information extraction
- Product catalog generation
- API response formatting

## Usage Patterns

### Basic Pattern

```python
from mirascope import llm, prompt_template
from pydantic import BaseModel

@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template("Your prompt here: {input}")
def your_function(input: str):
    pass
```

### With Response Model

```python
class YourResponse(BaseModel):
    field1: str
    field2: int

@llm.call(provider="openai", model="gpt-4o-mini", response_model=YourResponse)
@prompt_template("Extract data from: {text}")
def extract_data(text: str):
    pass
```

### With Dynamic Configuration

```python
from mirascope.core import BaseDynamicConfig

@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template("Process: {data}")
def process_data(data: str, temperature: float = 0.7) -> BaseDynamicConfig:
    return {
        "call_params": {
            "temperature": temperature
        }
    }
```

## Best Practices

1. **Choose the right technique**: Match the prompting style to your task complexity
2. **Be specific**: Clear instructions yield better results
3. **Use structured outputs**: When you need reliable data formats
4. **Iterate and test**: Refine prompts based on outputs
5. **Consider context limits**: Keep prompts concise but complete

## Performance Tips

- **Zero-shot** is fastest but may be less accurate
- **Few-shot** adds tokens but improves consistency
- **Role-based** can improve quality for specialized tasks
- **Chain-of-thought** increases token usage but improves reasoning
- **Structured output** may require more specific models (GPT-4 typically better)

## Common Pitfalls

- **Over-prompting**: Adding unnecessary complexity
- **Under-specifying**: Being too vague with instructions
- **Format mismatches**: Not matching examples to desired output
- **Role confusion**: Conflicting personas or expertise levels
- **Reasoning gaps**: Not requesting enough intermediate steps 
