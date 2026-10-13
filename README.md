# AI Study Coach — Adaptive Learning Agent

An AI-powered command-line tutoring application that adjusts learning difficulty based on student performance.

Built with Python and Groq's LLM API.

## Overview

AI Study Coach guides a student through a three-round learning session. It generates explanations, asks practice questions, evaluates answers, and adjusts subsequent difficulty based on the evaluation results.

Unlike a static question generator, the application uses a feedback loop to determine what the student should learn next.

## Features

- AI-generated explanations at beginner, intermediate, and advanced levels
- Practice questions tailored to the topic and difficulty
- Structured answer evaluation with scores from 0 to 2
- Misconception-aware follow-up explanations
- Rule-based adaptive difficulty
- Session history and performance summary
- Retry handling for temporary API failures and empty responses
- Automated unit tests for difficulty progression

## How It Works

1. The student chooses a topic.
2. The LLM generates an explanation and practice question.
3. The student submits an answer.
4. The LLM evaluates the answer and returns structured feedback.
5. Python applies the adaptation rules:
   - **0/2:** Reduce difficulty, with a minimum of beginner.
   - **1/2:** Maintain difficulty.
   - **2/2:** Increase difficulty, with a maximum of advanced.
6. The next round uses the updated difficulty and available misconception feedback.
7. The application displays a session summary.

## Tech Stack

- Python
- Groq API
- GPT-OSS 20B
- python-dotenv
- unittest

## Project Structure

```text
ai-study-coach/
├── SRC/
│   ├── main.py
│   └── test_adaptation.py
├── .gitignore
├── requirements.txt
└── README.md
```

The `.env` file and virtual environment are excluded from version control.

## Setup

### 1. Clone the repository

```bash
git clone <YOUR-REPOSITORY-URL>
cd ai-study-coach
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 4. Configure your API key

Create a `.env` file in the project root:

```dotenv
GROQ_API_KEY=your_groq_api_key_here
```

You can obtain an API key from the GroqCloud Console.

### 5. Run the application

```bash
python3 SRC/main.py
```

## Testing

Run the unit tests from the `SRC` directory:

```bash
cd SRC
python3 -m unittest test_adaptation -v
```

Five adaptation-policy tests passed during development.

## Example Session

Topic: Python functions

| Round | Difficulty | Score |
|---|---|---|
| 1 | Beginner | 0/2 |
| 2 | Beginner | 2/2 |
| 3 | Intermediate | 2/2 |

Final score: **4/6**

Next selected difficulty: **Advanced**

This example demonstrates the system retaining beginner difficulty after an incorrect answer and advancing after subsequent correct answers.

## Architecture

The application separates four responsibilities:

- **LLM interface:** Communicates with Groq and handles retries.
- **Evaluation:** Requests and validates structured scoring feedback.
- **Adaptation policy:** Uses deterministic Python rules to select difficulty.
- **Session controller:** Coordinates the learning loop and tracks performance.

## Current Limitations

- LLM-generated evaluations may be inaccurate.
- Session history is stored in memory and is not persisted between runs.
- The terminal accepts single-line answers.
- Question variety and misconception targeting are not guaranteed.
- The application currently runs three rounds per session.
- The system does not independently verify generated educational content.

## Future Improvements

- Persistent learner profiles
- More sophisticated mastery tracking
- Question-history awareness to reduce repetition
- Multi-line code-answer support
- Web interface
- Additional evaluation and integration tests

## Project Purpose

This project explores how LLM-generated educational content can be combined with deterministic decision-making and session state to build an adaptive learning workflow.