from pydantic import BaseModel, Field


class TwinReply(BaseModel):
    reply: str = Field(
        description="The visitor-facing chat message from Arianne's digital twin."
    )
    suggestions: list[str] = Field(
        min_length=3,
        max_length=3,
        description=(
            "Exactly 3 short follow-up questions the visitor could type next "
            "about Arianne's career, background, skills, experience, or how to get in touch."
        ),
    )


class ValidationResult(BaseModel):
    approved: bool = Field(
        description="True when the twin reply is exclusively about Arianne's professional career."
    )
    reason: str = Field(description="Short explanation of the approval decision.")
    revision: str = Field(
        description=(
            "If approved is false, a professional rewrite that answers only allowed career "
            "topics and apologizes for anything unrelated. If approved is true, repeat the original reply."
        )
    )
