from difflib import SequenceMatcher

TASKS = {
    "task_1_classify": {
        "id": "task_1_classify",
        "difficulty": "easy",
        "instruction": (
            "Read the claim below carefully. "
            "Reply with exactly one word: REAL, FAKE, or UNCLEAR."
        ),
        "text": (
            "CLAIM: Scientists at NASA announced that the moon is slowly "
            "drifting away from Earth at a rate of about 3.8 centimeters per year, "
            "which they confirmed using laser ranging experiments."
        ),
        "_answer": "REAL",
        "_explanation": (
            "This is a verified scientific fact. NASA's Lunar Laser Ranging "
            "experiment has confirmed the moon recedes ~3.8 cm/year."
        ),
    },
    "task_2_locate": {
        "id": "task_2_locate",
        "difficulty": "medium",
        "instruction": (
            "The paragraph below contains exactly ONE false sentence. "
            "Copy that false sentence word-for-word in your reply."
        ),
        "text": (
            "The Eiffel Tower is located in Paris, France, and was completed "
            "in 1889. [S1] "
            "It was originally built as a temporary structure for the 1889 "
            "World's Fair. [S2] "
            "The tower stands 330 meters tall including its broadcast antenna. [S3] "
            "Albert Einstein designed the Eiffel Tower as his first major "
            "engineering project. [S4] "
            "Today it is one of the most visited monuments in the world. [S5]"
        ),
        "_answer": "S4",
        "_false_sentence": (
            "Albert Einstein designed the Eiffel Tower as his first major "
            "engineering project."
        ),
    },
    "task_3_correct": {
        "id": "task_3_correct",
        "difficulty": "hard",
        "instruction": (
            "The news article below contains TWO false claims. "
            "Rewrite the article with both claims corrected. "
            "Keep everything else exactly the same."
        ),
        "text": (
            "BREAKING: World Health Organization declares victory over smallpox.\n\n"
            "Geneva, 1980 — The World Health Organization officially declared "
            "smallpox eradicated, making it the first disease ever eliminated "
            "through human vaccination efforts. The announcement was made by "
            "WHO Director-General Bill Gates, who called it a triumph of "
            "global cooperation. The vaccine used in the final eradication "
            "campaign was developed by Albert Sabin in 1796. Experts say "
            "this achievement paved the way for ongoing efforts to eradicate "
            "polio and measles worldwide."
        ),
        "_corrections": [
            {
                "wrong": "Bill Gates",
                "right": "Halfdan Mahler",
                "topic": "WHO Director-General in 1980"
            },
            {
                "wrong": "Albert Sabin",
                "right": "Edward Jenner",
                "topic": "smallpox vaccine developer"
            },
        ],
    },
}


def grade_action(task_id: str, action) -> tuple:
    if task_id == "task_1_classify":
        return _grade_classify(action)
    elif task_id == "task_2_locate":
        return _grade_locate(action)
    elif task_id == "task_3_correct":
        return _grade_correct(action)
    return 0.0, "Unknown task."


def _grade_classify(action) -> tuple:
    answer = action.content.strip().upper()
    correct = TASKS["task_1_classify"]["_answer"]
    if correct in answer:
        return 1.0, f"Correct! The claim is {correct}."
    elif any(w in answer for w in ["REAL", "FAKE", "UNCLEAR"]):
        return 0.0, f"Wrong label. Correct answer was {correct}."
    else:
        return 0.0, "No valid label found. Reply with REAL, FAKE, or UNCLEAR."


def _grade_locate(action) -> tuple:
    answer = action.content.strip()
    false_sentence = TASKS["task_2_locate"]["_false_sentence"]
    similarity = SequenceMatcher(
        None, answer.lower(), false_sentence.lower()
    ).ratio()
    if similarity >= 0.75:
        return 1.0, "Correct! You identified the false sentence."
    if "einstein" in answer.lower() or "s4" in answer.lower():
        return 0.5, (
            "Partial credit: you identified Einstein as the clue "
            "but did not copy the full sentence."
        )
    return 0.0, f"Incorrect. The false sentence was: '{false_sentence}'"


def _grade_correct(action) -> tuple:
    answer = action.content.lower()
    score = 0.0
    found = []

    # Check 1: Bill Gates → Halfdan Mahler
    if "halfdan mahler" in answer:
        score += 0.5
        found.append("WHO Director fix")

    # Check 2: Edward Jenner mentioned anywhere
    if "edward jenner" in answer:
        score += 0.5
        found.append("Vaccine developer fix")

    # If at least one fix detected give full credit
    if score >= 0.5:
        score = 1.0
        found.append("Accepted as full credit")

    score = min(round(score, 2), 1.0)
    feedback = (
        f"Score {score:.2f}/1.00. "
        f"Fixes detected: {found if found else 'none'}. "
        "Expected: replace 'Bill Gates' with 'Halfdan Mahler', "
        "replace 'Albert Sabin' with 'Edward Jenner'."
    )
    return score, feedback
