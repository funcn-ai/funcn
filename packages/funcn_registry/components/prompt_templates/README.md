# Mirascope Prompt Engineering Templates

This collection provides comprehensive examples of prompt engineering techniques using Mirascope's functional approach. Each template demonstrates best practices for building robust, type-safe, and observable LLM applications.

## 📚 Template Categories

### 1. Text-Based Prompts (`/text_based`)

Fundamental prompting techniques for single LLM calls.

- **Zero-Shot**: Direct prompting without examples
- **Few-Shot**: Learning from provided examples
- **Role-Based**: Assigning specific personas/roles
- **Chain-of-Thought**: Step-by-step reasoning
- **Structured Output**: Generating validated, structured data

### 2. Chaining-Based Prompts (`/chaining_based`)

Dynamic prompt composition and multi-step workflows.

- **Sequential Chain**: Linear step-by-step processing
- **Parallel Chain**: Concurrent LLM calls for efficiency
- **Conditional Chain**: Branching logic based on outputs
- **Iterative Chain**: Refinement through multiple passes
- **Multi-Step Reasoning**: Complex problem decomposition

### 3. Common Patterns (`/common_patterns`)

Reusable patterns for frequent use cases.

- **Summarization**: Content condensation techniques
- **Classification**: Categorization and labeling
- **Extraction**: Information and entity extraction
- **Question Answering**: Context-based Q&A
- **Content Generation**: Creative and structured content

### 4. Advanced Techniques (`/advanced_techniques`)

Sophisticated strategies for complex reasoning.

- **Tree of Thought**: Exploring multiple solution paths
- **Self-Consistency**: Multiple reasoning paths for reliability
- **Chain of Verification**: Systematic answer verification
- **Rephrase and Respond**: Query reformulation for clarity
- **Meta-Prompting**: Self-improving prompt generation

## 🎯 When to Use Each Technique

### Text-Based Prompts

| Technique | Best For | Example Use Case |
|-----------|----------|------------------|
| Zero-Shot | Simple, well-defined tasks | Basic Q&A, simple transformations |
| Few-Shot | Tasks requiring specific format/style | Custom formatting, domain-specific outputs |
| Role-Based | Tasks needing expertise or perspective | Technical analysis, creative writing |
| Chain-of-Thought | Complex reasoning or math problems | Problem-solving, logical deduction |
| Structured Output | Data extraction and validation | Form filling, API responses |

### Chaining-Based Prompts

| Technique | Best For | Example Use Case |
|-----------|----------|------------------|
| Sequential | Multi-stage processing | Document analysis → Summary → Action items |
| Parallel | Independent sub-tasks | Multi-language translation, parallel analysis |
| Conditional | Decision trees | Customer support routing, adaptive workflows |
| Iterative | Quality refinement | Content improvement, optimization |
| Multi-Step | Complex decomposition | Research tasks, comprehensive analysis |

### Common Patterns

| Pattern | Best For | Example Use Case |
|---------|----------|------------------|
| Summarization | Long content reduction | Meeting notes, article summaries |
| Classification | Categorization tasks | Sentiment analysis, content moderation |
| Extraction | Finding specific info | Named entities, key points |
| Q&A | Knowledge retrieval | FAQ systems, documentation queries |
| Generation | Content creation | Blog posts, product descriptions |

### Advanced Techniques

| Technique | Best For | Example Use Case |
|-----------|----------|------------------|
| Tree of Thought | Complex problem-solving | Mathematical proofs, strategic planning |
| Self-Consistency | High-stakes decisions | Medical diagnosis, legal analysis |
| Chain of Verification | Accuracy-critical tasks | Fact-checking, data validation |
| Rephrase & Respond | Ambiguous queries | Search queries, user questions |
| Meta-Prompting | Prompt optimization | Automated prompt engineering |

## 🚀 Quick Start

```python
from mirascope import llm, prompt_template
from mirascope.core import BaseDynamicConfig
from pydantic import BaseModel

# Example: Using Chain-of-Thought for problem solving
@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template(
    '''
    Solve this step by step:
    
    {problem}
    
    Think through each step carefully and show your work.
    '''
)
def solve_problem(problem: str):
    pass

# Example: Using structured output for data extraction
class ExtractedInfo(BaseModel):
    name: str
    email: str
    topic: str

@llm.call(provider="openai", model="gpt-4o-mini", response_model=ExtractedInfo)
@prompt_template("Extract contact info from: {text}")
def extract_contact(text: str):
    pass
```

## 📋 Best Practices

1. **Always use type hints** - Ensures type safety and better IDE support
2. **Define response models** - Use Pydantic for structured, validated outputs
3. **Implement proper error handling** - Gracefully handle LLM failures
4. **Add observability** - Use `@lilypad.trace()` for monitoring
5. **Keep prompts modular** - One prompt template per function
6. **Use computed fields** - Dynamic prompt construction with `BaseDynamicConfig`
7. **Prefer async** - Use `async def` for scalability
8. **Document thoroughly** - Clear docstrings and examples

## 🔧 Integration Tips

### With Agents

```python
from mirascope import llm
from mirascope.core import BaseAgent

class ResearchAgent(BaseAgent):
    """Agent that uses various prompt templates."""
    
    async def research(self, topic: str):
        # Use tree of thought for exploration
        thought_tree = await tree_of_thought.explore_topic(topic)
        
        # Verify findings
        verified = await chain_of_verification.verify_answer(
            thought_tree.best_solution
        )
        
        # Generate final report
        return await content_generation.create_report(verified)
```

### With Tools

```python
# Combine prompt templates with tool usage
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    tools=[web_search, calculator],
    response_model=AnalysisResult
)
@prompt_template(
    '''
    Analyze {topic} using available tools.
    Follow chain-of-thought reasoning.
    '''
)
async def analyze_with_tools(topic: str):
    pass
```

## 📊 Performance Considerations

- **Parallel chains** are fastest for independent tasks
- **Sequential chains** ensure order but add latency
- **Tree-based techniques** are computationally intensive
- **Iterative techniques** may require multiple LLM calls
- **Use caching** when appropriate for repeated prompts

## 🤝 Contributing

When adding new templates:

1. Follow the functional pattern (no classes unless necessary)
2. Include comprehensive docstrings
3. Add type hints for all parameters
4. Provide usage examples
5. Document when to use (and when not to use)
6. Add appropriate test cases

For questions or suggestions, please open an issue or reach out to the team.

## 📖 Additional Resources

- [Mirascope Documentation](https://mirascope.com/docs)
- [Mirascope Prompt Engineering Guide](https://mirascope.com/docs/mirascope/guides/prompt-engineering/)
- [Lilypad Documentation](https://lilypad.com/docs)

---

These templates are living examples - feel free to adapt, extend, and improve them for your specific use cases! 
