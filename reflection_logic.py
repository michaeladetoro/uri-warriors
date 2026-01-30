import random

# --- 1. In-Memory Dataset ---
# A small set of non-clinical reflective questions simulating a simplified RAG database.
REFLECTION_DATASET = [
    {
        "id": 0,
        "text": "Tell me more about something that challenged you recently.",
        "category": "challenge"
    },
    {
        "id": 1,
        "text": "How has your day-to-day life been affected recently?",
        "category": "impact"
    },
    {
        "id": 2,
        "text": "Is there a moment this week that made you feel a strong emotion?",
        "category": "emotion"
    },
    {
        "id": 3,
        "text": "If you could look at this situation from a distance, what would you notice?",
        "category": "perspective"
    },
    {
        "id": 4,
        "text": "What would you like to carry forward from this reflection?",
        "category": "closing"
    }
]

# --- 2. Response Style Guidelines ---
RESPONSE_GUIDELINES = (
    "1. Acknowledge emotion only: Mirror the user's emotional tone nicely.\n"
    "2. Avoid advice or reassurance: Do not try to fix the problem.\n"
    "3. Brevity: Keep the response under 8 seconds of spoken time.\n"
    "4. Forbidden: Never ask 'why'."
)

# --- 3. Session Rules ---
SESSION_RULES = {
    "max_questions": 5,
    "forbidden_words": ["why"],
    "closing_statement": "Thank you for sharing. I hope this reflection was helpful. Goodbye."
}

def get_next_action(current_state, question_count):
    """
    Decides the next move for the AI based on the session state.
    Simulates a RAG system retrieving the most appropriate next question.

    Args:
        current_state (str): The current flow state (e.g., 'Intro', 'Reflecting').
        question_count (int): How many questions have been asked so far.

    Returns:
        dict: {
            'next_question': str or None,
            'response_style': str,
            'should_close': bool
        }
    """
    # Check termination condition
    if question_count >= SESSION_RULES["max_questions"]:
        return {
            "next_question": None,
            "response_style": "Neutral, closing tone.",
            "should_close": True
        }
    
    # logic to select question (Simulated RAG)
    # In a real app, we would embed the user's last response and find the closest question.
    # Here, we sequentially iterate through our curated list based on question_count.
    
    try:
        # Ensure we don't go out of bounds if count exceeds dataset
        dataset_index = question_count 
        if dataset_index >= len(REFLECTION_DATASET):
            # Fallback for extended sessions
            fallback_questions = ["What else is coming up?", "Can you say more about that?"]
            selected_question = random.choice(fallback_questions)
        else:
            selected_question = REFLECTION_DATASET[dataset_index]["text"]
            
    except Exception as e:
        selected_question = "What else is on your mind?"

    # Check for forbidden words in our generated/selected question (Safety check)
    for word in SESSION_RULES["forbidden_words"]:
        if word in selected_question.lower().split():
            # If we accidentally picked a 'why' question, replace it
            selected_question = "What led to that feeling?"

    return {
        "next_question": selected_question,
        "response_style": RESPONSE_GUIDELINES,
        "should_close": False
    }
