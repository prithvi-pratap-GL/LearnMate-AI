from detoxify import Detoxify
from app.config.settings import settings

model = Detoxify("original")


def check_toxicity(text: str):
    scores = model.predict(text)

    risk = max(
        scores["toxicity"],
        scores["severe_toxicity"],
        scores["threat"],
        scores["identity_attack"],
        scores["insult"],
    )

    return risk < settings.TOXICITY_THRESHOLD, float(risk)