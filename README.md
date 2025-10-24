# Agentic SDLC - Examples

Simple example of AI Agents that can automate SDLC artifact generation, `Source: Feature Idea` -> `Generated: User Stories` -> `Generated Acceptance Criteria`

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Copy environment template
cp .env.sample .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

### 3. Run the Agents

```bash
cd examples
```

#### Complete Workflow (Recommended)

Generate user stories AND acceptance criteria in one command:

```bash
python -m workflow 01  # Run workflow for file 01-...
python -m workflow 02  # Run workflow for file 02-...
python -m workflow 03  # Run workflow for file 03-...
```

#### Individual Agents

Run agents in isolation:

```bash
# Generate user stories from feature idea
python -m user_story 01

# Generate acceptance criteria from user stories
python -m ac_writer 01

# Generate AC directly from idea (skip stories check)
python -m ac_writer 01 --idea
```

## Project Structure

```
examples/
├── data/
│   ├── ideas/          # Input: Feature idea files
│   ├── stories/        # Output: Generated user stories
│   └── ac/             # Output: Generated acceptance criteria
├── ac_writer/          # AC generation agent
├── user_story/         # User story generation agent
├── workflow/           # Complete workflow orchestration
├── tools/              # Shared tools (file retrieval)
└── nodes/              # Reusable LangGraph nodes
```

## How It Works

1. **Feature Idea** → Vague business requirements (in `data/ideas/`)
2. **User Stories** → Structured Gherkin scenarios (generated in `data/stories/`)
3. **Acceptance Criteria** → Testable AC for each scenario (generated in `data/ac/`)

Each agent uses LangGraph for orchestration and GPT-4o-mini for generation.

## Example Files

Try the workflow with the included examples:

- `01-feat-pagination.md` - API pagination feature
- `02-feat-refresh-button.md` - UI refresh button feature
- `03-feat-dashboard.md` - Vague dashboard improvement request

## Help

```bash
python -m workflow --help
python -m user_story --help
python -m ac_writer --help
```
