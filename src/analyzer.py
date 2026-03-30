from __future__ import annotations

import math
import re
import statistics
import wave
from pathlib import Path


HESITATION_WORDS = {
    "um",
    "uh",
    "hmm",
    "erm",
    "ah",
    "like",
}

CONFUSION_PHRASES = {
    "i forgot",
    "can't remember",
    "cannot remember",
    "not sure",
    "what was",
    "where was",
    "lost my train of thought",
}

POSITIVE_PROTECTIVE_PHRASES = {
    "followed routine",
    "remembered all",
    "completed independently",
    "no issues",
    "felt normal",
}


def clean_words(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())


def split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[.!?]+", text) if part.strip()]


def lexical_diversity(words: list[str]) -> float:
    if not words:
        return 0.0
    return len(set(words)) / len(words)


def repetition_ratio(words: list[str]) -> float:
    if len(words) < 4:
        return 0.0
    repeated = 0
    for index in range(1, len(words)):
        if words[index] == words[index - 1]:
            repeated += 1
    return repeated / len(words)


def hesitation_ratio(words: list[str]) -> float:
    if not words:
        return 0.0
    hesitations = sum(1 for word in words if word in HESITATION_WORDS)
    return hesitations / len(words)


def count_confusion_phrases(text: str) -> int:
    lowered = text.lower()
    return sum(1 for phrase in CONFUSION_PHRASES if phrase in lowered)


def count_protective_phrases(text: str) -> int:
    lowered = text.lower()
    return sum(1 for phrase in POSITIVE_PROTECTIVE_PHRASES if phrase in lowered)


def filler_pause_count(text: str) -> int:
    return len(re.findall(r"\.\.\.|--|\(pause\)|\[pause\]", text.lower()))


def average_sentence_length(sentences: list[str]) -> float:
    if not sentences:
        return 0.0
    lengths = [len(clean_words(sentence)) for sentence in sentences]
    return statistics.mean(lengths) if lengths else 0.0


def estimate_audio_duration_seconds(audio_path: str | None) -> float | None:
    if not audio_path:
        return None

    path = Path(audio_path)
    if not path.exists() or path.suffix.lower() != ".wav":
        return None

    with wave.open(str(path), "rb") as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        if rate <= 0:
            return None
        return frames / float(rate)


def _normalize(value: float, low: float, high: float) -> float:
    if math.isclose(high, low):
        return 0.0
    clipped = max(low, min(value, high))
    return (clipped - low) / (high - low)


def analyze_screening(
    transcript: str,
    age: int,
    memory_task_score: int,
    caregiver_concern: int,
    audio_path: str | None = None,
) -> dict:
    words = clean_words(transcript)
    sentences = split_sentences(transcript)
    word_count = len(words)
    diversity = lexical_diversity(words)
    repetition = repetition_ratio(words)
    hesitation = hesitation_ratio(words)
    confusion = count_confusion_phrases(transcript)
    protective = count_protective_phrases(transcript)
    pause_markers = filler_pause_count(transcript)
    avg_sentence_words = average_sentence_length(sentences)
    duration_seconds = estimate_audio_duration_seconds(audio_path)
    speaking_rate = None

    if duration_seconds and duration_seconds > 0 and word_count > 0:
        speaking_rate = word_count / (duration_seconds / 60.0)

    feature_scores = {
        "age_risk": _normalize(age, 50, 85),
        "memory_risk": 1 - _normalize(memory_task_score, 3, 10),
        "caregiver_risk": _normalize(caregiver_concern, 1, 5),
        "diversity_risk": 1 - _normalize(diversity, 0.28, 0.65),
        "repetition_risk": _normalize(repetition, 0.0, 0.08),
        "hesitation_risk": _normalize(hesitation, 0.0, 0.08),
        "confusion_risk": _normalize(confusion, 0, 4),
        "pause_risk": _normalize(pause_markers, 0, 6),
        "sentence_risk": 1 - _normalize(avg_sentence_words, 6, 16),
    }

    if speaking_rate is not None:
        feature_scores["speaking_rate_risk"] = 1 - _normalize(speaking_rate, 80, 150)
    else:
        feature_scores["speaking_rate_risk"] = 0.35

    weights = {
        "age_risk": 0.08,
        "memory_risk": 0.24,
        "caregiver_risk": 0.16,
        "diversity_risk": 0.10,
        "repetition_risk": 0.09,
        "hesitation_risk": 0.08,
        "confusion_risk": 0.11,
        "pause_risk": 0.05,
        "sentence_risk": 0.04,
        "speaking_rate_risk": 0.05,
    }

    raw_risk = sum(feature_scores[name] * weight for name, weight in weights.items())
    mitigation = min(protective * 0.04, 0.12)
    risk_score = round(max(0.0, min(1.0, raw_risk - mitigation)) * 100, 1)

    if risk_score >= 70:
        category = "High Risk"
        narrative = "This screening shows several strong warning signals that warrant prompt follow-up."
        recommendation = "Recommend specialist referral, caregiver briefing, and longitudinal follow-up within 2 weeks."
        next_steps = [
            "Arrange specialist cognitive evaluation",
            "Share the screening summary with the caregiver",
            "Plan repeat monitoring on the next visit",
        ]
    elif risk_score >= 45:
        category = "Moderate Risk"
        narrative = "This screening shows meaningful early-warning signals that should be reviewed soon."
        recommendation = "Recommend formal screening, repeated speech checks, and a clinician review within 4 weeks."
        next_steps = [
            "Repeat screening within 2 to 4 weeks",
            "Review medication adherence and routine slips",
            "Escalate if caregiver concern or confusion increases",
        ]
    else:
        category = "Low Risk"
        narrative = "This screening shows limited immediate concern, with monitoring still recommended over time."
        recommendation = "Recommend routine monitoring, lifestyle guidance, and a repeat screening after 3 months."
        next_steps = [
            "Continue routine observation",
            "Repeat screening at the next follow-up",
            "Track any new confusion or hesitation markers",
        ]

    sample_quality = round(
        min(
            100.0,
            35
            + min(word_count, 90) / 90 * 35
            + min(len(sentences), 6) / 6 * 15
            + (15 if speaking_rate is not None else 0),
        ),
        1,
    )

    observed_markers = []
    if confusion >= 2:
        observed_markers.append("Multiple confusion phrases were detected")
    if hesitation >= 0.02:
        observed_markers.append("Noticeable hesitation markers appeared in speech")
    if repetition >= 0.02:
        observed_markers.append("Repeated phrasing pattern is present")
    if avg_sentence_words < 10:
        observed_markers.append("Sentence structure is relatively short and compressed")
    if caregiver_concern >= 4:
        observed_markers.append("Caregiver concern is elevated")
    if memory_task_score <= 5:
        observed_markers.append("Memory task performance is below the safer range")
    if speaking_rate is not None and speaking_rate < 95:
        observed_markers.append("Speaking rate is slower than the expected baseline")
    if not observed_markers:
        observed_markers.append("No major linguistic red flags were observed in this sample")

    top_drivers = sorted(feature_scores.items(), key=lambda item: item[1], reverse=True)[:4]
    driver_labels = {
        "age_risk": "Age profile",
        "memory_risk": "Memory task performance",
        "caregiver_risk": "Caregiver concern",
        "diversity_risk": "Low lexical diversity",
        "repetition_risk": "Word repetition",
        "hesitation_risk": "Hesitation frequency",
        "confusion_risk": "Confusion markers",
        "pause_risk": "Pause markers",
        "sentence_risk": "Short sentence structure",
        "speaking_rate_risk": "Slow speaking rate",
    }

    feature_summary = {
        "Word count": word_count,
        "Lexical diversity": round(diversity, 3),
        "Repetition ratio": round(repetition, 3),
        "Hesitation ratio": round(hesitation, 3),
        "Confusion phrases": confusion,
        "Pause markers": pause_markers,
        "Avg sentence length": round(avg_sentence_words, 1),
        "Speaking rate (wpm)": round(speaking_rate, 1) if speaking_rate is not None else "N/A",
    }

    return {
        "risk_score": risk_score,
        "category": category,
        "narrative": narrative,
        "recommendation": recommendation,
        "next_steps": next_steps,
        "sample_quality": sample_quality,
        "observed_markers": observed_markers,
        "top_drivers": [driver_labels[name] for name, _ in top_drivers],
        "feature_scores": feature_scores,
        "feature_summary": feature_summary,
    }
