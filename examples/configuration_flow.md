# How sygaldry Configuration Works

This example demonstrates the complete flow of adding a component to your project.

## Step 1: Project Configuration (sygaldry.json)

When you run `sygaldry init`, it creates a `sygaldry.json` file:

```json
{
  "$schema": "./sygaldry.schema.json",
  "agentDirectory": "src/agents",
  "toolDirectory": "src/tools",
  "promptTemplateDirectory": "src/prompts",
  "responseModelDirectory": "src/models",
  "evalDirectory": "src/evals",
  "aliases": {
    "agents": "@/agents",
    "tools": "@/tools",
    "prompts": "@/prompts"
  },
  "defaultProvider": "openai",
  "defaultModel": "gpt-4o-mini",
  "stream": false
}
```

## Step 2: Component Structure in Registry

Each component in the registry has this structure:

```
packages/sygaldry_registry/components/tools/pdf_search/
├── component.json    # Metadata and configuration
├── tool.py          # Main implementation with {{template_vars}}
├── __init__.py      # Python module exports
└── sygaldry.md        # Documentation
```

## Step 3: Component Metadata (component.json)

The `component.json` tells the CLI what to do:

```json
{
  "name": "pdf_search_tool",  // Note the _tool suffix
  "type": "tool",
  "description": "Search within PDF documents",
  "files_to_copy": [
    {"source": "tool.py", "destination": "tool.py"},
    {"source": "__init__.py", "destination": "__init__.py"},
    {"source": "sygaldry.md", "destination": "sygaldry.md"}
  ],
  "target_directory_key": "toolDirectory",
  "python_dependencies": [
    {"name": "PyPDF2", "version": ">=3.0.0"}
  ],
  "template_variables": {
    "provider": "{{provider}}",
    "model": "{{model}}"
  },
  "supports_lilypad": true
}
```

## Step 4: Template Variables in Code

The component code contains template variables:

```python
# tool.py (before processing)
def search_pdf_content(file_path: str, query: str) -> str:
    """Search within a PDF document for the given query."""
    # Tool implementation
    return f"Searching for '{query}' in {file_path}"

# agent.py (before processing) - uses the tool
from mirascope import llm, prompt_template

@llm.call(provider="{{provider}}", model="{{model}}", tools=[search_pdf_content])
@prompt_template("Analyze this PDF content: {content}")
async def analyze_pdf(content: str) -> str:
    """Analyze PDF content using LLM with access to search tool."""
    ...
```

## Step 5: CLI Command Processing

When you run:
```bash
sygaldry add pdf_search_tool --provider anthropic --model claude-3-opus --with-lilypad
```

The CLI:

1. Reads your `sygaldry.json` to find `toolDirectory: "src/tools"`
2. Downloads the component from the registry
3. Replaces template variables:
   - `{{provider}}` → `anthropic`
   - `{{model}}` → `claude-3-opus`
4. Adds Lilypad decorators if `--with-lilypad` is specified
5. Copies files to `src/tools/pdf_search/`
6. Installs dependencies (`PyPDF2>=3.0.0`)

## Step 6: Final Result in Your Project

Your project structure becomes:

```
your_project/
├── sygaldry.json
└── src/
    └── tools/
        └── pdf_search/
            ├── __init__.py
            ├── tool.py      # With your customizations applied
            └── sygaldry.md     # Documentation for reference
```

The processed files:

```python
# tool.py (after processing)
from lilypad import trace  # Added because of --with-lilypad

@trace()  # Added because of --with-lilypad
def search_pdf_content(file_path: str, query: str) -> str:
    """Search within a PDF document for the given query."""
    # Tool implementation
    return f"Searching for '{query}' in {file_path}"

# agent.py (after processing) - if this were an agent component
from mirascope import llm, prompt_template
from lilypad import trace

@trace()  # Added because of --with-lilypad
@llm.call(provider="anthropic", model="claude-3-opus", tools=[search_pdf_content])
@prompt_template("Analyze this PDF content: {content}")
async def analyze_pdf(content: str) -> str:
    """Analyze PDF content using LLM with access to search tool."""
    ...
```

## Step 7: Using the Component

Now you can import and use the component:

```python
from src.tools.pdf_search import search_pdf_content, PDFSearchArgs

# The component uses YOUR specified provider and model
result = await search_pdf_content(PDFSearchArgs(
    file_path="research.pdf",
    query="machine learning algorithms"
))
```

## Key Points

1. **sygaldry.json** defines WHERE components go in your project
2. **component.json** defines WHAT gets copied and HOW
3. **Template variables** allow customization during installation
4. **sygaldry.md** provides documentation that stays with the component
5. Components become part of YOUR codebase, not external dependencies

This approach gives you:

- Full control over the code
- Proper Mirascope patterns out of the box
- Customization at installation time
- Documentation that travels with the code
- No framework lock-in 
