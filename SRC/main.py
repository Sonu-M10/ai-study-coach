
import os
import time
import json

from groq import Groq, APIStatusError, APITimeoutError, APIConnectionError
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("GROQ_API_KEY is missing from .env")

# Disable SDK retries because we handle retries ourselves
client = Groq(
    api_key=api_key,
    max_retries=0,
    timeout=20.0
)

MODEL = "openai/gpt-oss-20b"


def ask_llm(prompt):
    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=1200,
                reasoning_effort="low"
            )

            choice = response.choices[0]
            response_text = choice.message.content

            if response_text and response_text.strip():
                return response_text.strip()

            print(
                "Empty LLM response. "
                f"Finish reason: {choice.finish_reason}"
            )

        except APIStatusError as error:
            if error.status_code not in (429, 500, 502, 503, 504):
                raise

            print(f"Temporary API error: {error.status_code}")

        except (APITimeoutError, APIConnectionError) as error:
            print(f"Connection issue: {type(error).__name__}")

        if attempt < max_attempts - 1:
            wait_time = 2 ** (attempt + 1)
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

    raise RuntimeError(
        "The LLM could not produce a usable response after 3 attempts."
    )


def evaluate_answer(question, student_answer):
    prompt = (
        "You are a fair educational evaluator.\n"
        f"Question: {question}\n"
        f"Student answer: {student_answer}\n\n"
        "Return ONLY valid JSON with exactly these fields:\n"
        '"score": integer 0, 1, or 2,\n'
        '"feedback": a short explanation,\n'
        '"misconception": the main mistake or an empty string.\n'
        "Scoring: 0 = incorrect, 1 = partially correct, 2 = correct.\n"
        "Do not include Markdown formatting or code fences."
    )

    response_text = ask_llm(prompt)
    evaluation = json.loads(response_text)

    score = evaluation.get("score")

    if type(score) is not int or score not in (0, 1, 2):
        raise ValueError("Invalid evaluation score.")

    if not isinstance(evaluation.get("feedback"), str):
        raise ValueError("Invalid evaluation feedback.")

    if not isinstance(evaluation.get("misconception"), str):
        raise ValueError("Invalid misconception.")

    return evaluation


def update_difficulty(current_difficulty, score):
    if score == 0:
        return max(1, current_difficulty - 1)

    elif score == 2:
        return min(3, current_difficulty + 1)

    return current_difficulty


def main():
    print("Welcome to AI Study Coach!")

    topic = input("What would you like to learn? ").strip()

    if not topic:
        print("Please enter a topic.")
        return

    session = {
        "topic": topic,
        "difficulty": 1,
        "history": []
    }

    difficulty_names = {
        1: "beginner",
        2: "intermediate",
        3: "advanced"
    }

    misconception = ""

    try:
        for round_number in range(1, 4):
            difficulty = session["difficulty"]
            level = difficulty_names[difficulty]

            print(f"\n--- Round {round_number}/3 ---")
            print(f"Difficulty: {level}")

            explanation_prompt = (
                f"You are a concise Python tutor. "
                f"Teach the topic '{topic}' at a {level} level. "
                "Use no more than 120 words total. "
                "Include one short practical example. "
                "Avoid tables, long lists, and lengthy introductions. "
                f"If relevant, correct this misconception: {misconception}"
            )

            print("\nGenerating explanation...\n")
            explanation = ask_llm(explanation_prompt)
            print(explanation)

            question_prompt = (
                f"Write exactly ONE {level}-level practice question "
                f"about '{topic}' based on this explanation:\n"
                f"{explanation}\n\n"
                "The question must be answerable in one line of text. "
                "Prefer conceptual questions or predicting code output. "
                "Do not ask the student to write a multiline function. "
                "Keep the question under 60 words. "
                "Do not include the answer."
            )

            print("\nPractice question:\n")
            question = ask_llm(question_prompt)
            print(question)

            student_answer = input("\nYour answer: ").strip()

            if not student_answer:
                print("No answer submitted. Ending session.")
                break

            print("\nEvaluating...\n")
            evaluation = evaluate_answer(question, student_answer)

            score = evaluation["score"]
            misconception = evaluation["misconception"]

            print(f"Score: {score}/2")
            print(f"Feedback: {evaluation['feedback']}")

            if misconception:
                print(f"Misconception: {misconception}")

            session["history"].append({
                "round": round_number,
                "difficulty": difficulty,
                "question": question,
                "answer": student_answer,
                "score": score,
                "feedback": evaluation["feedback"],
                "misconception": misconception
            })

            session["difficulty"] = update_difficulty(
                difficulty, score
            )

            if score == 0:
                print("\nNext action: Review the misconception.")
            elif score == 1:
                print("\nNext action: Reinforce understanding.")
            else:
                print("\nNext action: Increase difficulty if possible.")

        print("\n========== SESSION SUMMARY ==========")

        history = session["history"]

        if history:
            total_score = sum(item["score"] for item in history)
            maximum_score = len(history) * 2

            print(f"Topic: {session['topic']}")
            print(f"Questions completed: {len(history)}")
            print(f"Total score: {total_score}/{maximum_score}")
            print(
                f"Final difficulty: "
                f"{difficulty_names[session['difficulty']]}"
            )

            for item in history:
                print(
                    f"Round {item['round']}: "
                    f"{item['score']}/2 "
                    f"({difficulty_names[item['difficulty']]})"
                )
        else:
            print("No questions completed.")

    except APIStatusError as error:
        print(f"\nGroq API error ({error.status_code}): {error}")

    except json.JSONDecodeError:
        print("\nThe LLM returned invalid JSON.")

    except Exception as error:
        print(f"\nAn unexpected error occurred: {error}")


if __name__ == "__main__":
    main()
