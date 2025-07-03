# Common Prompt Patterns

Common patterns represent reusable prompt templates for frequently encountered tasks. These patterns provide tested approaches for standard NLP tasks that can be adapted to specific use cases.

## Templates Overview

### 1. Summarization (`summarization.py`)

Various techniques for condensing content while preserving key information.

**When to use:**

- Long document condensation
- Meeting notes synthesis
- Article abstracts
- Report summaries

**Techniques included:**

- **Extractive**: Select key sentences
- **Abstractive**: Generate new summary text
- **Hierarchical**: Multi-level summaries
- **Aspect-based**: Focus on specific aspects

**Key parameters:**

- Summary length (words/sentences)
- Detail level (brief/detailed)
- Focus areas
- Target audience

### 2. Classification (`classification.py`)

Categorization and labeling of text into predefined or dynamic categories.

**When to use:**

- Content moderation
- Sentiment analysis
- Topic categorization
- Intent detection

**Techniques included:**

- **Binary**: Yes/no classification
- **Multi-class**: Multiple exclusive categories
- **Multi-label**: Multiple applicable labels
- **Hierarchical**: Nested categories

**Key parameters:**

- Category definitions
- Confidence thresholds
- Example mappings
- Edge case handling

### 3. Extraction (`extraction.py`)

Information and entity extraction from unstructured text.

**When to use:**

- Named entity recognition
- Key information extraction
- Data mining
- Form filling

**Techniques included:**

- **Entity extraction**: Names, dates, locations
- **Relationship extraction**: Connections between entities
- **Attribute extraction**: Properties and characteristics
- **Pattern matching**: Structured data extraction

**Key parameters:**

- Entity types to extract
- Extraction rules
- Validation criteria
- Output structure

### 4. Question Answering (`question_answering.py`)

Context-based question answering with various strategies.

**When to use:**

- FAQ systems
- Documentation queries
- Knowledge retrieval
- Conversational interfaces

**Techniques included:**

- **Extractive QA**: Answer from context
- **Generative QA**: Generate new answers
- **Multi-hop QA**: Reason across multiple sources
- **Conversational QA**: Context-aware dialogue

**Key parameters:**

- Context sources
- Answer length
- Confidence requirements
- Citation needs

### 5. Content Generation (`content_generation.py`)

Creative and structured content creation.

**When to use:**

- Blog post writing
- Product descriptions
- Marketing copy
- Technical documentation

**Techniques included:**

- **Template-based**: Fill structured templates
- **Free-form**: Creative generation
- **Style transfer**: Adapt to specific styles
- **Expansion**: Elaborate on outlines

**Key parameters:**

- Content type
- Target length
- Style guidelines
- SEO requirements

## Usage Examples

### Summarization

```python
from sygaldry_registry.components.prompt_templates.common_patterns import summarization

# Basic summary
summary = await summarization.summarize_text(
    text=long_article,
    max_words=100,
    style="bullet_points"
)

# Hierarchical summary
hierarchical = await summarization.hierarchical_summary(
    document=report,
    levels=["executive", "detailed", "technical"]
)
```

### Classification

```python
from sygaldry_registry.components.prompt_templates.common_patterns import classification

# Multi-label classification
labels = await classification.multi_label_classify(
    text=customer_feedback,
    categories=["bug", "feature_request", "praise", "complaint"],
    threshold=0.7
)

# Hierarchical classification
category = await classification.hierarchical_classify(
    text=article,
    taxonomy=news_taxonomy
)
```

### Extraction

```python
from sygaldry_registry.components.prompt_templates.common_patterns import extraction

# Entity extraction
entities = await extraction.extract_entities(
    text=document,
    entity_types=["person", "organization", "date", "money"]
)

# Structured extraction
structured_data = await extraction.extract_structured(
    text=email,
    schema=ContactInfoSchema
)
```

## Best Practices by Pattern

### Summarization

- Preserve factual accuracy
- Maintain key relationships
- Consider audience needs
- Avoid hallucination

### Classification

- Provide clear category definitions
- Include boundary examples
- Handle ambiguous cases
- Set appropriate thresholds

### Extraction

- Define extraction schemas clearly
- Validate extracted data
- Handle missing information
- Normalize output formats

### Question Answering

- Verify answer accuracy
- Cite sources when possible
- Handle "unknown" gracefully
- Maintain context awareness

### Content Generation

- Follow brand guidelines
- Ensure factual accuracy
- Maintain consistency
- Optimize for purpose

## Customization Guide

### Adapting Templates

```python
# Extend existing pattern
class CustomSummarizer(BaseSummarizer):
    def __init__(self, domain_knowledge: dict):
        super().__init__()
        self.domain = domain_knowledge
    
    async def summarize(self, text: str) -> Summary:
        # Add domain-specific logic
        enhanced_prompt = self.enhance_with_domain(text)
        return await super().summarize(enhanced_prompt)
```

### Combining Patterns

```python
# Chain multiple patterns
async def analyze_document(doc: str) -> Analysis:
    # Extract key information
    entities = await extraction.extract_entities(doc)
    
    # Classify document type
    doc_type = await classification.classify_document(doc)
    
    # Generate appropriate summary
    summary = await summarization.summarize_by_type(
        doc, doc_type, entities
    )
    
    return Analysis(
        entities=entities,
        type=doc_type,
        summary=summary
    )
```

## Performance Considerations

| Pattern | Token Usage | Latency | Accuracy Requirements |
|---------|-------------|---------|----------------------|
| Summarization | Medium-High | Medium | High |
| Classification | Low | Low | Medium-High |
| Extraction | Medium | Low-Medium | Very High |
| Q&A | Variable | Medium | High |
| Generation | High | High | Medium |

## Common Pitfalls and Solutions

### Summarization

- **Pitfall**: Loss of critical details
- **Solution**: Use importance scoring

### Classification

- **Pitfall**: Overlapping categories
- **Solution**: Use confidence scores

### Extraction

- **Pitfall**: Missing context
- **Solution**: Expand extraction window

### Question Answering

- **Pitfall**: Hallucinated answers
- **Solution**: Require citations

### Content Generation

- **Pitfall**: Generic output
- **Solution**: Add specific examples 
