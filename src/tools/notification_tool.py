from agents import function_tool
from tools.implementation.notification import record_user_details, record_unknown_question

@function_tool
def record_user_details(email: str, name: str, notes: str) -> str:
    """
    Use this tool to record that a user is interested in being in touch and provided an email address
    Args:
        email: The email address of this user
        name: The user's name, if they provided it
        notes: Any additional info about the conversation that's worth recording to give context
    """
    record_user_details(email, name, notes)
    return "Email sent successfully"

@function_tool
def record_unknown_question(question: str) -> str:
    """
    Always use this tool to record any question that couldn't be answered as you didn't know the answer
    Args:
        question: The question that couldn't be answered
    """
    record_unknown_question(question)
    return "Question recorded successfully"
