"""SIOP Deterministic Second-Rater — Codebook implementation.

Implements all 30 feature scoring functions described in
``final_analysis_outputs/SIOP_Codebook_and_Python_Pipeline.md``.

Each ``score_fN(text, ...)`` returns ``(score, diagnostics_dict)`` where
``score`` is an integer 0-4 and ``diagnostics_dict`` exposes the indicator
counts that drove the decision (so disagreements with the human rater are
interpretable).

Three features have cross-feature cap rules that are applied during a final
post-processing pass in :func:`apply_cross_feature_caps`:

* F23 (content-objective alignment) is capped at 2 if F1 ≤ 1.
* F24 (language-objective alignment) is capped at 2 if F2 ≤ 1.
* F27 (vocabulary review) is capped at 1 if F9 == 0.
"""

from __future__ import annotations

import re
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    import textstat as _textstat
except Exception:  # pragma: no cover
    _textstat = None


def _flesch_kincaid(text: str) -> float | None:
    """Robust FK grade level. Returns None if textstat / its corpora are unavailable."""
    if not text or _textstat is None:
        return None
    try:
        return float(_textstat.flesch_kincaid_grade(text))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------

def split_sections(text: str) -> dict[str, str]:
    """Split text into opening (top 25%), middle, closing (bottom 25%), full."""
    n = len(text)
    if n == 0:
        return {"opening": "", "middle": "", "closing": "", "full": ""}
    return {
        "opening": text[: n // 4],
        "middle": text[n // 4 : 3 * n // 4],
        "closing": text[3 * n // 4 :],
        "full": text,
    }


def section_coverage(text: str, patterns: list[str]) -> int:
    """Number of sections (opening/middle/closing) where ANY pattern matches."""
    secs = split_sections(text)
    hits = 0
    for sec_name in ("opening", "middle", "closing"):
        if any(re.search(p, secs[sec_name], re.IGNORECASE) for p in patterns):
            hits += 1
    return hits


def count_distinct_categories(
    text: str, category_patterns: dict[str, list[str]]
) -> int:
    """Number of indicator categories with at least one match."""
    return sum(
        1
        for _, pats in category_patterns.items()
        if any(re.search(p, text, re.IGNORECASE) for p in pats)
    )


def total_hits(text: str, patterns: list[str]) -> int:
    return sum(len(re.findall(p, text, re.IGNORECASE)) for p in patterns)


def all_patterns(category_patterns: dict[str, list[str]]) -> list[str]:
    return [p for pats in category_patterns.values() for p in pats]


def map_score(distinct: int, hits: int, sec_cov: int, integration: bool) -> int:
    """Generic 0-4 mapping per Part 2 of the codebook."""
    if hits == 0:
        return 0
    if distinct <= 1 and sec_cov <= 1 and not integration:
        return 1
    if distinct == 1 and (hits >= 2 or sec_cov == 1):
        return 2
    if distinct >= 2 and sec_cov >= 2:
        if distinct >= 3 and integration:
            return 4
        return 3
    return 1


def _generic_score(
    text: str,
    cats: dict[str, list[str]],
    integration_key: str | None = None,
) -> tuple[int, dict[str, Any]]:
    distinct = count_distinct_categories(text, cats)
    hits = sum(total_hits(text, p) for p in cats.values())
    sec_cov = section_coverage(text, all_patterns(cats))
    integration = bool(
        integration_key
        and any(
            re.search(p, text, re.IGNORECASE) for p in cats.get(integration_key, [])
        )
    )
    score = map_score(distinct, hits, sec_cov, integration)
    diag = {
        "distinct": distinct,
        "hits": hits,
        "sec_cov": sec_cov,
        "integration": integration,
    }
    return score, diag


# ---------------------------------------------------------------------------
# Component 1 — Lesson Preparation
# ---------------------------------------------------------------------------

def score_f1_content_objectives(text: str) -> tuple[int, dict[str, Any]]:
    cats = {
        "header": [
            r"\bcontent\s+objective[s]?\s*[:\-]",
            r"\blearning\s+(objective|target|goal)[s]?\s*[:\-]",
        ],
        "swbat": [
            r"\bSWBAT\b",
            r"\bstudents?\s+will\s+be\s+able\s+to\b",
            r"\bI\s+(can|will\s+be\s+able\s+to)\b",
        ],
        "verb": [
            r"\b(analyze|identify|describe|explain|compare|evaluate|design|"
            r"investigate|construct|develop|interpret|model)\b"
        ],
        "display": [
            r"\b(post|display|review\s+at\s+(start|end)|visible|on\s+the\s+board)\b"
        ],
    }
    score, diag = _generic_score(text, cats, integration_key="header")
    has_header = diag["integration"]
    has_learning_header = bool(
        re.search(cats["header"][1], text, re.IGNORECASE)
    )
    if not has_header and not has_learning_header:
        score = min(score, 2)
    diag["cap_applied"] = (not has_header) and (not has_learning_header)
    return score, diag


def score_f2_language_objectives(text: str) -> tuple[int, dict[str, Any]]:
    cats = {
        "header": [r"\blanguage\s+objective[s]?\s*[:\-]"],
        "lang_function": [
            r"\b(use|describe|explain|compare|argue|justify)\b[^\n]{0,80}"
            r"\b(sentence\s+frames?|academic\s+language|in\s+(oral|written))\b"
        ],
        "domain_target": [
            r"\b(academic\s+(vocabulary|language)|sentence\s+structure|"
            r"discourse\s+function|language\s+(skill|use|practice))\b"
        ],
        "display": [
            r"\b(post|display|review\s+at\s+(start|end)|visible|on\s+the\s+board)\b"
            r"[^\n]{0,80}\blanguage"
        ],
        "frames": [r"\bsentence\s+(frames?|stems?|starters?)\b"],
    }
    score, diag = _generic_score(text, cats, integration_key="header")
    has_header = diag["integration"]
    only_frames = (
        not has_header
        and not re.search(cats["domain_target"][0], text, re.IGNORECASE)
        and not re.search(cats["lang_function"][0], text, re.IGNORECASE)
    )
    if only_frames:
        score = min(score, 2)
    diag["cap_applied"] = only_frames
    return score, diag


def score_f3_age_appropriate(
    text: str, stated_grade: int | None = None
) -> tuple[int, dict[str, Any]]:
    has_grade = bool(
        re.search(
            r"\b(grade|grade\s+level)\s*[:\-]?\s*(K|kindergarten|\d{1,2})\b",
            text,
            re.IGNORECASE,
        )
    )
    has_standard = bool(
        re.search(
            r"\b\d\.[A-Z]\d[A-Z]\d\.\d|\bNGSS\b|\bCCSS\b|\bMS[\-\s]\w+|\bHS[\-\s]\w+|"
            r"\bAZ\s+ELP\b",
            text,
        )
    )
    fk_grade = _flesch_kincaid(text)

    score = 2
    if has_grade:
        score = 3
    if has_grade and has_standard:
        score = 4
    if (
        stated_grade is not None
        and fk_grade is not None
        and abs(fk_grade - stated_grade) > 4
    ):
        score = max(score - 1, 1)
    return score, {
        "fk": round(fk_grade, 2) if fk_grade is not None else None,
        "has_grade": has_grade,
        "has_standard": has_standard,
    }


def score_f4_supplementary_materials(text: str) -> tuple[int, dict[str, Any]]:
    cats = {
        "visuals": [
            r"\b(visual[s]?|image[s]?|diagram[s]?|chart[s]?|poster[s]?|anchor\s+chart)\b"
        ],
        "multimedia": [
            r"\b(video[s]?|audio|recording|animation|simulation|interactive)\b"
        ],
        "models_realia": [
            r"\b(model[s]?|realia|specimen[s]?|artifact[s]?|3D|hands[\-\s]on)\b"
        ],
        "texts": [
            r"\b(text[s]?|article[s]?|reading|handout[s]?|worksheet[s]?)\b"
        ],
        "technology": [
            r"\b(computer[s]?|tablet[s]?|app[s]?|software|website|digital)\b"
        ],
        "manipulatives": [r"\b(manipulative[s]?|blocks?|cards?|tiles?|cubes?)\b"],
        "organizers": [
            r"\b(graphic\s+organizer[s]?|venn|t[\-\s]chart|concept\s+map|flow\s*chart)\b"
        ],
    }
    distinct = count_distinct_categories(text, cats)
    if distinct == 0:
        score = 0
    elif distinct == 1:
        score = 1
    elif distinct == 2:
        score = 2
    elif distinct in (3, 4):
        score = 3
    else:
        score = 4
    return score, {"distinct": distinct}


def score_f5_content_adaptation(text: str) -> tuple[int, dict[str, Any]]:
    cats = {
        "proficiency_naming": [
            r"\b(beginning|emerging|developing|expanding|bridging|reaching|"
            r"elementary|intermediate|advanced)\s+(proficiency|level|learner)"
        ],
        "tiered": [
            r"\b(tiered|leveled|differentiated|scaffolded\s+versions?|"
            r"three\s+versions?|multiple\s+levels?)\b"
        ],
        "modified_text": [
            r"\b(modified\s+text|simplified\s+text|adapted\s+text)\b"
        ],
        "l1_support": [
            r"\b(translation|home\s+language|L1|native\s+language|bilingual)\b"
        ],
    }
    score, diag = _generic_score(text, cats, integration_key="proficiency_naming")
    return score, diag


def score_f6_meaningful_activities(text: str) -> tuple[int, dict[str, Any]]:
    reading = bool(
        re.search(
            r"\b(read(ing)?|article[s]?|text[s]?|passage|book[s]?)\b",
            text,
            re.IGNORECASE,
        )
    )
    writing = bool(
        re.search(
            r"\b(writ(e|ing)|journal|essay|notes?|note[\-\s]?taking|"
            r"reflection|paragraph|report|describe\s+in\s+writing)\b",
            text,
            re.IGNORECASE,
        )
    )
    listening = bool(
        re.search(
            r"\b(listen(ing)?|video[s]?|audio|lecture|presentation|podcast)\b",
            text,
            re.IGNORECASE,
        )
    )
    speaking = bool(
        re.search(
            r"\b(speak(ing)?|discuss(ion)?|share\s+out|present(ation)?|"
            r"oral|talk|conversation|debate)\b",
            text,
            re.IGNORECASE,
        )
    )
    concept_tied = bool(
        re.search(
            r"\b(concept|content|topic|standard|objective|principle)\b",
            text,
            re.IGNORECASE,
        )
    )
    modalities = sum([reading, writing, listening, speaking])
    score = modalities
    if not concept_tied and score > 1:
        score = max(score - 1, 1)
    return score, {
        "R": reading,
        "W": writing,
        "L": listening,
        "S": speaking,
        "concept_tied": concept_tied,
    }


# ---------------------------------------------------------------------------
# Component 2 — Building Background
# ---------------------------------------------------------------------------

def score_f7_background_links(text: str) -> tuple[int, dict[str, Any]]:
    cats = {
        "personal_experience": [
            r"\b(think\s+about\s+a\s+time|have\s+you\s+ever|"
            r"in\s+your\s+(experience|life|community|home|family|culture)|"
            r"remember\s+a\s+time|when\s+you\s+were)\b"
        ],
        "cultural": [
            r"\b(cultur(e|al)|tradition[s]?|heritage|background|community|"
            r"funds?\s+of\s+knowledge)\b"
        ],
        "real_world": [
            r"\b(real[\-\s]world|everyday|daily\s+life|familiar|relevant\s+to\s+(students|their\s+lives))\b"
        ],
        "brainstorm_share": [
            r"\b(brainstorm|share\s+(your|out|with))\b[^\n]{0,40}"
            r"\b(experience|memory|home|culture|tradition)\b"
        ],
    }
    score, diag = _generic_score(text, cats, integration_key="cultural")
    return score, diag


def score_f8_past_learning(text: str) -> tuple[int, dict[str, Any]]:
    cats = {
        "time_deictics": [
            r"\b(yesterday|last\s+(week|class|lesson|time)|previously|"
            r"earlier\s+(we|today)|recall|as\s+we\s+(discussed|learned|saw)|"
            r"building\s+on)\b"
        ],
        "prior_knowledge": [
            r"\b(prior\s+knowledge|what\s+(you|do\s+you)\s+(already\s+)?know|"
            r"activate|access\s+prior)\b"
        ],
        "word_wall_anchor": [
            r"\b(word\s+wall|anchor\s+chart|previous(ly)?)\b"
        ],
        "spiral_review": [
            r"\b(review\s+(of|the)|recap|warm[\-\s]up|do\s+now|bell\s+ringer)\b"
        ],
    }
    return _generic_score(text, cats, integration_key="prior_knowledge")


def score_f9_key_vocabulary(text: str) -> tuple[int, dict[str, Any]]:
    cats = {
        "header": [
            r"\b(vocabulary|key\s+(terms?|vocabulary|words?))\s*[:\-]"
        ],
        "preteach": [
            r"\bpre[\-\s]?teach",
            r"\bintroduce[^\n]{0,40}\b(vocabulary|terms?|words?)\b",
        ],
        "word_wall": [
            r"\bword\s+wall",
            r"\bvocabulary\s+(wall|chart|list|bank)",
        ],
        "repetition": [
            r"\buse[^\n]{0,40}\bnew\s+(words?|vocabulary|terms?)\b",
            r"\brepeat(ed)?\s+(exposure|use)\b",
            r"\bpractice[^\n]{0,40}\bvocabulary\b",
        ],
        "visual_vocab": [
            r"\bflash\s*cards?\b",
            r"\bpictures?\s+(with|next\s+to)\s+(words?|terms?)\b",
            r"\bvisual[^\n]{0,40}\bvocabulary\b",
        ],
        "quoted_terms": [
            r"['\"][a-zA-Z\-]{4,}['\"]",
            r"\*\*[a-zA-Z\-]{4,}\*\*",
        ],
    }
    distinct = count_distinct_categories(text, cats)
    if distinct == 0:
        score = 0
    elif distinct == 1:
        score = 1
    elif distinct == 2:
        score = 2
    elif distinct == 3:
        score = 3
    else:
        score = 4
    return score, {"distinct": distinct}


# ---------------------------------------------------------------------------
# Component 3 — Comprehensible Input
# ---------------------------------------------------------------------------

def score_f10_speech_appropriate(text: str) -> tuple[int, dict[str, Any]]:
    cats = {
        "captions": [
            r"\b(closed\s+caption[s]?|transcript[s]?|subtitle[s]?)\b"
        ],
        "slower_speech": [
            r"\b(slower|slow\s+down|enunciate|clearly\s+pronounce|speak\s+slowly)\b"
        ],
        "simplified_syntax": [
            r"\b(simple\s+(sentence|language)|short\s+sentences|simplified)\b"
        ],
        "paraphrase": [
            r"\b(paraphrase|restate|rephrase|in\s+other\s+words)\b"
        ],
        "comprehensible": [
            r"\b(comprehensible\s+input|comprehensible\s+language)\b"
        ],
    }
    score, diag = _generic_score(text, cats, integration_key="comprehensible")
    has_protocol = bool(
        re.search(r"\b(speech\s+modification|teacher\s+talk\s+protocol)\b",
                  text, re.IGNORECASE)
    )
    if not has_protocol:
        score = min(score, 3)
    diag["partial_recovery_cap_applied"] = not has_protocol
    return score, diag


def score_f11_clear_task_explanation(text: str) -> tuple[int, dict[str, Any]]:
    cats = {
        "numbered_steps": [
            r"\bstep\s*\d+\b",
            r"(?m)^\s*\d+\.\s",
            r"\bfirst\b[^\n]{0,80}\bthen\b[^\n]{0,80}\b(finally|last)\b",
        ],
        "time_durations": [r"\(\s*\d+\s*minutes?\s*\)", r"\b\d+\s*minutes?\b"],
        "modeling": [
            r"\b(model|demonstrate|show\s+how|"
            r"I\s+do[^\n]{0,30}we\s+do[^\n]{0,30}you\s+do|"
            r"gradual\s+release)\b"
        ],
        "rubric_expectations": [
            r"\b(rubric|criteria|success\s+criteria|expectations|directions)\b"
        ],
    }
    return _generic_score(text, cats, integration_key="numbered_steps")


def score_f12_variety_techniques(text: str) -> tuple[int, dict[str, Any]]:
    cats = {
        "visuals": [r"\b(visual[s]?|image[s]?|diagram[s]?|chart[s]?|poster[s]?)\b"],
        "multimedia": [r"\b(video[s]?|audio|animation|simulation|interactive)\b"],
        "models_realia": [r"\b(model[s]?|realia|specimen[s]?|3D|hands[\-\s]on)\b"],
        "texts": [r"\b(text[s]?|article[s]?|reading|handout[s]?)\b"],
        "technology": [r"\b(computer[s]?|tablet[s]?|app[s]?|software|digital)\b"],
        "modeling": [r"\b(model|demonstrate|think[\-\s]?aloud)\b"],
        "gestures": [
            r"\b(gestures?|body\s+language|TPR|total\s+physical\s+response)\b"
        ],
    }
    distinct = count_distinct_categories(text, cats)
    if distinct == 0:
        score = 0
    elif distinct in (1, 2):
        score = 1
    elif distinct == 3:
        score = 2
    elif distinct == 4:
        score = 3
    else:
        score = 4
    return score, {"distinct": distinct}


# ---------------------------------------------------------------------------
# Component 4 — Strategies
# ---------------------------------------------------------------------------

def score_f13_learning_strategies(text: str) -> tuple[int, dict[str, Any]]:
    cats = {
        "metacognitive": [
            r"\b(metacogniti(ve|on)|"
            r"think\s+about\s+(your|how)\s+(thinking|you\s+learn)|"
            r"reflection|reflect\s+on)\b"
        ],
        "cognitive": [
            r"\b(predict|summariz|infer|visualiz|connect|question.*text)\b"
        ],
        "note_taking": [
            r"\b(notes?|note[\-\s]?taking|interactive\s+notebook|graphic\s+organizer)\b"
        ],
        "self_monitoring": [
            r"\b(self[\-\s]?(assess|monitor|check)|exit\s+ticket|reflection)\b"
        ],
    }
    return _generic_score(text, cats, integration_key="metacognitive")


def score_f14_scaffolding(text: str) -> tuple[int, dict[str, Any]]:
    cats = {
        "frames": [
            r"\bsentence\s+(frames?|stems?|starters?)\b",
            r"_____",
        ],
        "word_banks": [
            r"\b(word\s+bank|glossary|vocabulary\s+list)\b"
        ],
        "modeling": [
            r"\b(model|demonstrate|think[\-\s]?aloud|teacher\s+models?)\b"
        ],
        "organizers": [
            r"\b(graphic\s+organizer|anchor\s+chart|t[\-\s]chart|venn|concept\s+map)\b"
        ],
        "gradual_release": [
            r"\bI\s+do[^\n]{0,30}we\s+do[^\n]{0,30}you\s+do\b",
            r"\bgradual\s+release\b",
        ],
        "chunking": [
            r"\b(chunk|partial\s+outline|guided\s+notes|cloze)\b"
        ],
    }
    return _generic_score(text, cats, integration_key="frames")


def score_f15_higher_order(text: str) -> tuple[int, dict[str, Any]]:
    higher_bloom = re.findall(
        r"\b(analyze|evaluate|create|synthesi[sz]e|justify|argue|design|"
        r"hypothesi[sz]e|critique|compose|construct|formulate|appraise|defend)\b",
        text,
        re.IGNORECASE,
    )
    lower_bloom = re.findall(
        r"\b(remember|recall|list|name|identify|state|define|recognize|repeat)\b",
        text,
        re.IGNORECASE,
    )
    open_questions = re.findall(
        r"\b(how\s+(does|do|might|could)|why\s+(does|do|might|is|are)|"
        r"what\s+if|what\s+would\s+happen)\b",
        text,
        re.IGNORECASE,
    )
    compare_tasks = re.findall(
        r"\b(compare|contrast|differen(ce|tiate))\b", text, re.IGNORECASE
    )
    explicit_q_header = bool(
        re.search(
            r"\b(open[\-\s]?ended|analytical|reflective|exploratory|"
            r"interpret(ive|ation))\s+questions?\b",
            text,
            re.IGNORECASE,
        )
    )
    argumentation = bool(
        re.search(
            r"\b(argue|justify|defend|claim.*evidence|CER\b)\b",
            text,
            re.IGNORECASE,
        )
    )

    cats_present = sum(
        [
            len(higher_bloom) > 0,
            len(open_questions) > 0,
            len(compare_tasks) > 0,
            explicit_q_header,
            argumentation,
        ]
    )

    diag = {
        "higher_bloom": len(higher_bloom),
        "lower_bloom": len(lower_bloom),
        "open_q": len(open_questions),
        "compare": len(compare_tasks),
        "q_header": explicit_q_header,
        "argumentation": argumentation,
        "cats_present": cats_present,
    }

    if (
        len(higher_bloom) == 0
        and not open_questions
        and not explicit_q_header
        and len(lower_bloom) > 0
    ):
        return 1, diag

    if cats_present == 0:
        score = 0
    elif cats_present == 1:
        score = 1
    elif cats_present == 2:
        score = 3 if explicit_q_header else 2
    elif cats_present == 3:
        score = 3
    else:
        score = 4
    return score, diag


# ---------------------------------------------------------------------------
# Component 5 — Interaction
# ---------------------------------------------------------------------------

def score_f16_interaction(text: str) -> tuple[int, dict[str, Any]]:
    cats = {
        "pair": [r"\b(pair[s]?|partner[s]?|in\s+pairs|with\s+a\s+partner)\b"],
        "small_group": [
            r"\b(small\s+group[s]?|in\s+groups?|group\s+of\s+\d|group\s+work)\b"
        ],
        "whole_class": [
            r"\b(whole[\-\s]class|class\s+discussion|share\s+out|table\s+talk)\b"
        ],
        "elaborated": [
            r"\b(explain[^\n]{0,30}reasoning|extend[^\n]{0,30}answer|elaborate|"
            r"why\s+do\s+you\s+think)\b"
        ],
        "protocols": [
            r"\b(turn\s+and\s+talk|think[\-\s]?pair[\-\s]?share|jigsaw|fishbowl|"
            r"gallery\s+walk)\b"
        ],
    }
    return _generic_score(text, cats, integration_key="protocols")


def score_f17_grouping(text: str) -> tuple[int, dict[str, Any]]:
    cats = {
        "rationale": [
            r"\bgroup(ing|ed)\s+(by|to|for|based\s+on)\b"
        ],
        "multiple_types": [
            r"\b(whole[\-\s]class|small\s+group|pair[s]?|partner[s]?|individual)\b"
        ],
        "heterogeneous": [
            r"\b(mixed[\-\s]?(level|proficiency|ability)|heterogen|"
            r"with\s+(native\s+English\s+)?speakers)\b"
        ],
        "roles": [
            r"\b(role[s]?|recorder|reporter|facilitator|timekeeper)\b"
        ],
    }
    return _generic_score(text, cats, integration_key="rationale")


def score_f18_wait_time(text: str) -> tuple[int, dict[str, Any]]:
    """NOT recoverable from text in general — binary detection only."""
    has_wait = bool(
        re.search(r"\b(wait\s+time|think\s+time)\b", text, re.IGNORECASE)
    )
    has_duration = bool(
        re.search(
            r"\b(wait|think)\s+time[^\n]{0,40}\d+\s*(seconds?|minutes?)",
            text,
            re.IGNORECASE,
        )
    )
    if has_wait and has_duration:
        return 3, {"detected": True, "duration": True}
    if has_wait:
        return 1, {"detected": True, "duration": False}
    return 0, {"detected": False, "duration": False}


def score_f19_l1_clarification(text: str) -> tuple[int, dict[str, Any]]:
    cats = {
        "l1_use": [
            r"\b(L1|home\s+language|native\s+language|first\s+language|"
            r"primary\s+language)\b"
        ],
        "bilingual_peer": [
            r"\b(bilingual\s+(peer|aide|partner|buddy)|"
            r"translation\s+(partner|peer))\b"
        ],
        "translated_materials": [
            r"\b(translated|translation|"
            r"bilingual\s+(text|materials?|glossary|resources?))\b"
        ],
        "l1_brainstorm": [
            r"\b(discuss[^\n]{0,30}home\s+language|brainstorm[^\n]{0,30}L1|"
            r"use[^\n]{0,30}native\s+language\s+to)\b"
        ],
    }
    return _generic_score(text, cats, integration_key="l1_use")


# ---------------------------------------------------------------------------
# Component 6 — Practice & Application
# ---------------------------------------------------------------------------

def score_f20_hands_on(text: str) -> tuple[int, dict[str, Any]]:
    cats = {
        "lab_equipment": [
            r"\b(beaker|flask|microscope|thermometer|balance|scale|test\s+tube|"
            r"petri\s+dish|graduated\s+cylinder|hand\s+lens|magnifier|magnet[s]?)\b"
        ],
        "construction": [
            r"\b(foam|clay|cardboard|paper|string|rope|tape|glue|popsicle|recycled)\b"
        ],
        "manipulatives": [
            r"\b(blocks?|cubes?|tiles?|counters?|cards?|chips|bead[s]?)\b"
        ],
        "kits": [r"\b(FOSS|STC|Amplify|Mystery\s+Science|kit)\b"],
        "realia": [
            r"\b(realia|specimen[s]?|live|actual\s+object[s]?|real\s+(thing|object))\b"
        ],
        "action_verbs": [
            r"\b(build|construct|measure|observe|dissect|manipulate|test)\b"
        ],
    }
    score, diag = _generic_score(text, cats, integration_key="lab_equipment")
    physical_action = (
        diag["distinct"]
        - (1 if re.search(cats["action_verbs"][0], text, re.IGNORECASE) else 0)
    )
    only_video = bool(
        re.search(r"\b(video|watch)\b", text, re.IGNORECASE)
    ) and physical_action <= 0
    if only_video:
        score = min(score, 1)
    diag["only_video_cap"] = only_video
    return score, diag


def score_f21_application_content_language(text: str) -> tuple[int, dict[str, Any]]:
    content_app = bool(
        re.search(
            r"\b(apply[^\n]{0,40}\b(concept|principle|idea|content)|"
            r"new\s+context|real[\-\s]world\s+(application|task)|"
            r"transfer|extend[^\n]{0,40}(idea|concept))\b",
            text,
            re.IGNORECASE,
        )
    )
    language_app = bool(
        re.search(
            r"\b(use\s+(academic\s+language|new\s+vocabulary|sentence\s+frames?)|"
            r"oral\s+presentation|written\s+explanation|"
            r"convey[^\n]{0,40}(content|concept))\b",
            text,
            re.IGNORECASE,
        )
    )
    if content_app and language_app:
        score = 4
    elif content_app or language_app:
        score = 2
    else:
        score = 0
    return score, {"content_app": content_app, "language_app": language_app}


def score_f22_four_skills(text: str) -> tuple[int, dict[str, Any]]:
    skills = {
        "R": bool(
            re.search(
                r"\b(read(ing)?|article[s]?|text[s]?|passage|book[s]?)\b",
                text,
                re.IGNORECASE,
            )
        ),
        "W": bool(
            re.search(
                r"\b(writ(e|ing)|journal|essay|notes?|paragraph|report|label)\b",
                text,
                re.IGNORECASE,
            )
        ),
        "L": bool(
            re.search(
                r"\b(listen(ing)?|video[s]?|audio|lecture|presentation|podcast)\b",
                text,
                re.IGNORECASE,
            )
        ),
        "S": bool(
            re.search(
                r"\b(speak(ing)?|discuss(ion)?|share\s+out|present(ation)?|"
                r"oral|talk|conversation|debate)\b",
                text,
                re.IGNORECASE,
            )
        ),
    }
    return sum(skills.values()), skills


# ---------------------------------------------------------------------------
# Component 7 — Lesson Delivery
# ---------------------------------------------------------------------------

def _extract_objective(text: str, kind: str) -> str:
    """Pull out the content/language objective sentence for TF-IDF alignment.

    kind: 'content' | 'language'
    Returns '' if no explicit header is present.
    """
    pat = (
        r"(?:content\s+objective|learning\s+(?:objective|target|goal))s?\s*[:\-]\s*"
        r"([^\n\.]{10,300})"
        if kind == "content"
        else r"language\s+objective[s]?\s*[:\-]\s*([^\n\.]{10,300})"
    )
    m = re.search(pat, text, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _alignment_score(
    text: str, objective_text: str
) -> tuple[int, dict[str, Any]]:
    if not objective_text or len(objective_text) < 10:
        return 0, {"reason": "no objective"}
    activity_steps = re.split(
        r"(?im)\bstep\s*\d+|^\s*\d+\.\s|\n\n", text
    )
    activity_steps = [s for s in activity_steps if len(s) > 30]
    if not activity_steps:
        return 1, {"reason": "no steps"}
    docs = [objective_text] + activity_steps
    try:
        vec = TfidfVectorizer(stop_words="english")
        tfidf = vec.fit_transform(docs)
    except ValueError:
        return 1, {"reason": "tfidf failed"}
    sims = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
    aligned = int((sims >= 0.25).sum())
    ratio = aligned / len(activity_steps)
    if ratio == 0:
        score = 0
    elif ratio < 0.3:
        score = 1
    elif ratio < 0.5:
        score = 2
    elif ratio < 0.8:
        score = 3
    else:
        score = 4
    return score, {
        "ratio": round(ratio, 3),
        "aligned": aligned,
        "n_steps": len(activity_steps),
    }


def score_f23_content_alignment(text: str) -> tuple[int, dict[str, Any]]:
    obj = _extract_objective(text, "content")
    return _alignment_score(text, obj)


def score_f24_language_alignment(text: str) -> tuple[int, dict[str, Any]]:
    obj = _extract_objective(text, "language")
    return _alignment_score(text, obj)


def score_f25_engagement(text: str) -> tuple[int, dict[str, Any]]:
    active_verbs = re.findall(
        r"\bstudents?\s+(will|are|do|create|build|investigate|design|"
        r"explore|present|discuss|analyze|construct)\b",
        text,
        re.IGNORECASE,
    )
    pacing = re.findall(r"\b\d+\s*minutes?\b", text)
    multiple_phases = bool(
        re.search(
            r"\b(step\s*[2-9]|phase\s*[2-9]|then|next|after\s+that|finally)\b",
            text,
            re.IGNORECASE,
        )
    )
    long_passive = bool(
        re.search(
            r"\bwatch\s+the\s+entire\s+video|silent\s+reading\s+for\s+\d+",
            text,
            re.IGNORECASE,
        )
    )

    cats = (
        (len(active_verbs) >= 3)
        + (len(pacing) >= 1)
        + multiple_phases
        + (not long_passive)
    )
    score = min(cats, 4)
    return score, {
        "active_verbs": len(active_verbs),
        "pacing_markers": len(pacing),
        "multiple_phases": multiple_phases,
        "long_passive": long_passive,
    }


def score_f26_pacing(text: str) -> tuple[int, dict[str, Any]]:
    time_markers = re.findall(r"\b\d+\s*minutes?\b", text)
    has_total = bool(
        re.search(
            r"\b(total\s+(time|duration)|class\s+period|\d+\s*minute\s+lesson)\b",
            text,
            re.IGNORECASE,
        )
    )
    has_diff = bool(
        re.search(
            r"\b(fast\s+finishers?|early\s+finishers?|extension|additional\s+time)\b",
            text,
            re.IGNORECASE,
        )
    )
    n = len(time_markers)
    if n == 0:
        score = 0
    elif n == 1:
        score = 1
    elif n == 2:
        score = 2
    elif n in (3, 4):
        score = 3
    else:
        score = 4 if has_diff else 3
    return score, {
        "time_markers": n,
        "has_total": has_total,
        "has_differentiation": has_diff,
    }


# ---------------------------------------------------------------------------
# Component 8 — Review & Assessment
# ---------------------------------------------------------------------------

def score_f27_vocab_review(text: str) -> tuple[int, dict[str, Any]]:
    secs = split_sections(text)
    closing = secs["closing"]
    cats = {
        "closing_vocab_review": [
            r"\b(vocabulary|key\s+(terms?|words?))\b"
        ],
        "vocab_assessment": [
            r"\b(vocab(ulary)?\s+(test|quiz|assessment|check)|matching|"
            r"fill[\-\s]in[\-\s]the[\-\s]blank)\b"
        ],
        "word_wall_close": [
            r"\b(word\s+wall|anchor\s+chart|vocabulary\s+(wall|chart))\b"
        ],
    }
    distinct_close = sum(
        1
        for pats in cats.values()
        if any(re.search(p, closing, re.IGNORECASE) for p in pats)
    )
    repeated_use = bool(
        re.search(
            r"\b(repeat(ed)?\s+(exposure|use)|practice[^\n]{0,30}vocabulary|"
            r"use\s+new\s+(words?|terms?))\b",
            text,
            re.IGNORECASE,
        )
    )
    score = distinct_close + (1 if repeated_use else 0)
    score = min(score, 4)
    return score, {
        "distinct_close": distinct_close,
        "repeated_use": repeated_use,
    }


def score_f28_content_review(text: str) -> tuple[int, dict[str, Any]]:
    secs = split_sections(text)
    closing = secs["closing"]
    cats = {
        "closing_summary": [
            r"\b(summar(y|ize)|recap|review|wrap[\-\s]up|conclude|reflection)\b"
        ],
        "concept_check": [
            r"\b(check[s]?\s+for\s+understanding|exit\s+ticket|comprehension\s+check)\b"
        ],
        "objective_link": [
            r"\b(objective|goal|target)\b"
        ],
        "student_articulation": [
            r"\bstudents?\s+(explain|share|present|articulate|reflect\s+on)\s+"
            r"(what|their|the)\b"
        ],
    }
    distinct_close = sum(
        1
        for pats in cats.values()
        if any(re.search(p, closing, re.IGNORECASE) for p in pats)
    )
    distinct_full = count_distinct_categories(text, cats)
    score = max(distinct_close, distinct_full - 1)
    score = min(score, 4)
    return score, {
        "distinct_close": distinct_close,
        "distinct_full": distinct_full,
    }


def score_f29_feedback(text: str) -> tuple[int, dict[str, Any]]:
    cats = {
        "formative": [
            r"\b(feedback|formative\s+assessment|"
            r"check\s+for\s+understanding|monitoring)\b"
        ],
        "rubric": [r"\b(rubric|criteria|success\s+criteria)\b"],
        "peer_feedback": [
            r"\b(peer\s+(feedback|review|response)|partner\s+check)\b"
        ],
        "throughout": [
            r"\b(throughout|ongoing|continuous|frequent(ly)?)\s+"
            r"(feedback|check|monitor)\b"
        ],
    }
    score, diag = _generic_score(text, cats, integration_key="throughout")
    return score, diag


def score_f30_assessment_throughout(text: str) -> tuple[int, dict[str, Any]]:
    multiple_moments = bool(
        re.search(
            r"\b(check[s]?\s+for\s+understanding|formative|exit\s+ticket|"
            r"quick\s+(check|write)|thumbs\s+(up|down))\b",
            text,
            re.IGNORECASE,
        )
    )
    has_formative = multiple_moments
    has_summative = bool(
        re.search(
            r"\b(summative|final\s+assessment|test|quiz|"
            r"end[\-\s]of[\-\s](unit|lesson))\b",
            text,
            re.IGNORECASE,
        )
    )
    tied_to_objectives = bool(
        re.search(
            r"\bassess(ment)?[^\n]{0,80}(objective|goal|target)\b",
            text,
            re.IGNORECASE,
        )
    )
    diverse = sum(
        [
            bool(re.search(r"\boral|verbal\b", text, re.IGNORECASE)),
            bool(re.search(r"\bwritten|writ(e|ing)\b", text, re.IGNORECASE)),
            bool(
                re.search(
                    r"\bperformance|present(ation)?|demonstrat",
                    text,
                    re.IGNORECASE,
                )
            ),
        ]
    )
    cats = sum(
        [
            multiple_moments,
            has_formative and has_summative,
            tied_to_objectives,
            diverse >= 2,
        ]
    )
    score = min(cats, 4)
    return score, {
        "multiple_moments": multiple_moments,
        "formative": has_formative,
        "summative": has_summative,
        "tied_to_objectives": tied_to_objectives,
        "diverse_formats": diverse,
    }


# ---------------------------------------------------------------------------
# Registry + cross-feature caps
# ---------------------------------------------------------------------------

SCORERS = {
    1: score_f1_content_objectives,
    2: score_f2_language_objectives,
    3: score_f3_age_appropriate,
    4: score_f4_supplementary_materials,
    5: score_f5_content_adaptation,
    6: score_f6_meaningful_activities,
    7: score_f7_background_links,
    8: score_f8_past_learning,
    9: score_f9_key_vocabulary,
    10: score_f10_speech_appropriate,
    11: score_f11_clear_task_explanation,
    12: score_f12_variety_techniques,
    13: score_f13_learning_strategies,
    14: score_f14_scaffolding,
    15: score_f15_higher_order,
    16: score_f16_interaction,
    17: score_f17_grouping,
    18: score_f18_wait_time,
    19: score_f19_l1_clarification,
    20: score_f20_hands_on,
    21: score_f21_application_content_language,
    22: score_f22_four_skills,
    23: score_f23_content_alignment,
    24: score_f24_language_alignment,
    25: score_f25_engagement,
    26: score_f26_pacing,
    27: score_f27_vocab_review,
    28: score_f28_content_review,
    29: score_f29_feedback,
    30: score_f30_assessment_throughout,
}

FEATURE_NAMES = {
    1: "Content objectives clearly defined, displayed, reviewed",
    2: "Language objectives clearly defined, displayed, reviewed",
    3: "Content concepts age-appropriate",
    4: "Supplementary materials used to a high degree",
    5: "Content adaptation to all proficiency levels",
    6: "Meaningful activities integrating concepts and language",
    7: "Concepts linked to background experiences",
    8: "Past learning explicitly linked",
    9: "Key vocabulary emphasized",
    10: "Speech appropriate for proficiency [partial-recovery]",
    11: "Explanation of academic tasks clear",
    12: "Variety of techniques to make content clear",
    13: "Opportunities to use learning strategies",
    14: "Scaffolding techniques consistently used",
    15: "Higher-order thinking promoted",
    16: "Frequent opportunities for interaction",
    17: "Grouping configurations support objectives",
    18: "Sufficient wait time [excluded]",
    19: "Opportunities to clarify in L1",
    20: "Hands-on materials/manipulatives",
    21: "Application activities for content + language",
    22: "Activities integrate all four language skills",
    23: "Content objectives supported by delivery [partial-recovery]",
    24: "Language objectives supported by delivery [partial-recovery]",
    25: "Students engaged 90-100% [observation-dependent]",
    26: "Pacing appropriate [partial-recovery]",
    27: "Comprehensive review of key vocabulary",
    28: "Comprehensive review of key content concepts",
    29: "Regular feedback to students [partial-recovery]",
    30: "Assessment of comprehension throughout",
}

# Features the codebook flags for exclusion or partial-recovery treatment.
EXCLUDED_FEATURES = (18, 25)


def apply_cross_feature_caps(scores: dict[int, int]) -> dict[int, int]:
    """Apply cross-feature cap rules from the codebook."""
    out = dict(scores)
    if out.get(1, 4) <= 1:
        out[23] = min(out.get(23, 0), 2)
    if out.get(2, 4) <= 1:
        out[24] = min(out.get(24, 0), 2)
    if out.get(9, 4) == 0:
        out[27] = min(out.get(27, 0), 1)
    return out


def score_activity(text: str) -> tuple[dict[int, int], dict[int, dict[str, Any]]]:
    """Run all 30 scorers on a single activity text."""
    raw_scores: dict[int, int] = {}
    diags: dict[int, dict[str, Any]] = {}
    for fnum, fn in SCORERS.items():
        score, diag = fn(text)
        raw_scores[fnum] = int(score)
        diags[fnum] = diag
    final_scores = apply_cross_feature_caps(raw_scores)
    return final_scores, diags


# ---------------------------------------------------------------------------
# Evidence extraction + plain-language rationale
# ---------------------------------------------------------------------------
# Per-feature category → regex map. Mirrors (intentionally, for transparency)
# the patterns embedded inside each `score_fN_*` above. The Streamlit
# inspector uses this registry to (a) pull text excerpts that drove the
# algorithm's decision and (b) describe in plain English why the score was
# assigned. If you add or modify a scoring function, update the matching
# entry here so the inspector evidence stays in sync.

FEATURE_PATTERNS: dict[int, dict[str, list[str]]] = {
    1: {
        "header": [
            r"\bcontent\s+objective[s]?\s*[:\-]",
            r"\blearning\s+(objective|target|goal)[s]?\s*[:\-]",
        ],
        "swbat": [
            r"\bSWBAT\b",
            r"\bstudents?\s+will\s+be\s+able\s+to\b",
            r"\bI\s+(can|will\s+be\s+able\s+to)\b",
        ],
        "verb": [
            r"\b(analyze|identify|describe|explain|compare|evaluate|design|"
            r"investigate|construct|develop|interpret|model)\b"
        ],
        "display": [
            r"\b(post|display|review\s+at\s+(start|end)|visible|on\s+the\s+board)\b"
        ],
    },
    2: {
        "header": [r"\blanguage\s+objective[s]?\s*[:\-]"],
        "lang_function": [
            r"\b(use|describe|explain|compare|argue|justify)\b[^\n]{0,80}"
            r"\b(sentence\s+frames?|academic\s+language|in\s+(oral|written))\b"
        ],
        "domain_target": [
            r"\b(academic\s+(vocabulary|language)|sentence\s+structure|"
            r"discourse\s+function|language\s+(skill|use|practice))\b"
        ],
        "display": [
            r"\b(post|display|review\s+at\s+(start|end)|visible|on\s+the\s+board)\b"
            r"[^\n]{0,80}\blanguage"
        ],
        "frames": [r"\bsentence\s+(frames?|stems?|starters?)\b"],
    },
    3: {
        "grade_level": [
            r"\b(grade|grade\s+level)\s*[:\-]?\s*(K|kindergarten|\d{1,2})\b"
        ],
        "standards": [
            r"\b\d\.[A-Z]\d[A-Z]\d\.\d|\bNGSS\b|\bCCSS\b|\bMS[\-\s]\w+|"
            r"\bHS[\-\s]\w+|\bAZ\s+ELP\b"
        ],
    },
    4: {
        "visuals": [
            r"\b(visual[s]?|image[s]?|diagram[s]?|chart[s]?|poster[s]?|anchor\s+chart)\b"
        ],
        "multimedia": [
            r"\b(video[s]?|audio|recording|animation|simulation|interactive)\b"
        ],
        "models_realia": [
            r"\b(model[s]?|realia|specimen[s]?|artifact[s]?|3D|hands[\-\s]on)\b"
        ],
        "texts": [r"\b(text[s]?|article[s]?|reading|handout[s]?|worksheet[s]?)\b"],
        "technology": [
            r"\b(computer[s]?|tablet[s]?|app[s]?|software|website|digital)\b"
        ],
        "manipulatives": [r"\b(manipulative[s]?|blocks?|cards?|tiles?|cubes?)\b"],
        "organizers": [
            r"\b(graphic\s+organizer[s]?|venn|t[\-\s]chart|concept\s+map|flow\s*chart)\b"
        ],
    },
    5: {
        "proficiency_naming": [
            r"\b(beginning|emerging|developing|expanding|bridging|reaching|"
            r"elementary|intermediate|advanced)\s+(proficiency|level|learner)"
        ],
        "tiered": [
            r"\b(tiered|leveled|differentiated|scaffolded\s+versions?|"
            r"three\s+versions?|multiple\s+levels?)\b"
        ],
        "modified_text": [r"\b(modified\s+text|simplified\s+text|adapted\s+text)\b"],
        "l1_support": [
            r"\b(translation|home\s+language|L1|native\s+language|bilingual)\b"
        ],
    },
    6: {
        "reading": [r"\b(read(ing)?|article[s]?|text[s]?|passage|book[s]?)\b"],
        "writing": [
            r"\b(writ(e|ing)|journal|essay|notes?|note[\-\s]?taking|"
            r"reflection|paragraph|report|describe\s+in\s+writing)\b"
        ],
        "listening": [
            r"\b(listen(ing)?|video[s]?|audio|lecture|presentation|podcast)\b"
        ],
        "speaking": [
            r"\b(speak(ing)?|discuss(ion)?|share\s+out|present(ation)?|"
            r"oral|talk|conversation|debate)\b"
        ],
        "concept_tied": [
            r"\b(concept|content|topic|standard|objective|principle)\b"
        ],
    },
    7: {
        "personal_experience": [
            r"\b(think\s+about\s+a\s+time|have\s+you\s+ever|"
            r"in\s+your\s+(experience|life|community|home|family|culture)|"
            r"remember\s+a\s+time|when\s+you\s+were)\b"
        ],
        "cultural": [
            r"\b(cultur(e|al)|tradition[s]?|heritage|background|community|"
            r"funds?\s+of\s+knowledge)\b"
        ],
        "real_world": [
            r"\b(real[\-\s]world|everyday|daily\s+life|familiar|"
            r"relevant\s+to\s+(students|their\s+lives))\b"
        ],
        "brainstorm_share": [
            r"\b(brainstorm|share\s+(your|out|with))\b[^\n]{0,40}"
            r"\b(experience|memory|home|culture|tradition)\b"
        ],
    },
    8: {
        "time_deictics": [
            r"\b(yesterday|last\s+(week|class|lesson|time)|previously|"
            r"earlier\s+(we|today)|recall|as\s+we\s+(discussed|learned|saw)|"
            r"building\s+on)\b"
        ],
        "prior_knowledge": [
            r"\b(prior\s+knowledge|what\s+(you|do\s+you)\s+(already\s+)?know|"
            r"activate|access\s+prior)\b"
        ],
        "word_wall_anchor": [r"\b(word\s+wall|anchor\s+chart|previous(ly)?)\b"],
        "spiral_review": [
            r"\b(review\s+(of|the)|recap|warm[\-\s]up|do\s+now|bell\s+ringer)\b"
        ],
    },
    9: {
        "header": [r"\b(vocabulary|key\s+(terms?|vocabulary|words?))\s*[:\-]"],
        "preteach": [
            r"\bpre[\-\s]?teach",
            r"\bintroduce[^\n]{0,40}\b(vocabulary|terms?|words?)\b",
        ],
        "word_wall": [
            r"\bword\s+wall",
            r"\bvocabulary\s+(wall|chart|list|bank)",
        ],
        "repetition": [
            r"\buse[^\n]{0,40}\bnew\s+(words?|vocabulary|terms?)\b",
            r"\brepeat(ed)?\s+(exposure|use)\b",
            r"\bpractice[^\n]{0,40}\bvocabulary\b",
        ],
        "visual_vocab": [
            r"\bflash\s*cards?\b",
            r"\bpictures?\s+(with|next\s+to)\s+(words?|terms?)\b",
            r"\bvisual[^\n]{0,40}\bvocabulary\b",
        ],
        "quoted_terms": [
            r"['\"][a-zA-Z\-]{4,}['\"]",
            r"\*\*[a-zA-Z\-]{4,}\*\*",
        ],
    },
    10: {
        "captions": [r"\b(closed\s+caption[s]?|transcript[s]?|subtitle[s]?)\b"],
        "slower_speech": [
            r"\b(slower|slow\s+down|enunciate|clearly\s+pronounce|speak\s+slowly)\b"
        ],
        "simplified_syntax": [
            r"\b(simple\s+(sentence|language)|short\s+sentences|simplified)\b"
        ],
        "paraphrase": [r"\b(paraphrase|restate|rephrase|in\s+other\s+words)\b"],
        "comprehensible": [
            r"\b(comprehensible\s+input|comprehensible\s+language)\b"
        ],
        "protocol": [r"\b(speech\s+modification|teacher\s+talk\s+protocol)\b"],
    },
    11: {
        "numbered_steps": [
            r"\bstep\s*\d+\b",
            r"(?m)^\s*\d+\.\s",
            r"\bfirst\b[^\n]{0,80}\bthen\b[^\n]{0,80}\b(finally|last)\b",
        ],
        "time_durations": [r"\(\s*\d+\s*minutes?\s*\)", r"\b\d+\s*minutes?\b"],
        "modeling": [
            r"\b(model|demonstrate|show\s+how|"
            r"I\s+do[^\n]{0,30}we\s+do[^\n]{0,30}you\s+do|gradual\s+release)\b"
        ],
        "rubric_expectations": [
            r"\b(rubric|criteria|success\s+criteria|expectations|directions)\b"
        ],
    },
    12: {
        "visuals": [r"\b(visual[s]?|image[s]?|diagram[s]?|chart[s]?|poster[s]?)\b"],
        "multimedia": [r"\b(video[s]?|audio|animation|simulation|interactive)\b"],
        "models_realia": [r"\b(model[s]?|realia|specimen[s]?|3D|hands[\-\s]on)\b"],
        "texts": [r"\b(text[s]?|article[s]?|reading|handout[s]?)\b"],
        "technology": [r"\b(computer[s]?|tablet[s]?|app[s]?|software|digital)\b"],
        "modeling": [r"\b(model|demonstrate|think[\-\s]?aloud)\b"],
        "gestures": [
            r"\b(gestures?|body\s+language|TPR|total\s+physical\s+response)\b"
        ],
    },
    13: {
        "metacognitive": [
            r"\b(metacogniti(ve|on)|"
            r"think\s+about\s+(your|how)\s+(thinking|you\s+learn)|"
            r"reflection|reflect\s+on)\b"
        ],
        "cognitive": [
            r"\b(predict|summariz|infer|visualiz|connect|question.*text)\b"
        ],
        "note_taking": [
            r"\b(notes?|note[\-\s]?taking|interactive\s+notebook|graphic\s+organizer)\b"
        ],
        "self_monitoring": [
            r"\b(self[\-\s]?(assess|monitor|check)|exit\s+ticket|reflection)\b"
        ],
    },
    14: {
        "frames": [
            r"\bsentence\s+(frames?|stems?|starters?)\b",
            r"_____",
        ],
        "word_banks": [r"\b(word\s+bank|glossary|vocabulary\s+list)\b"],
        "modeling": [
            r"\b(model|demonstrate|think[\-\s]?aloud|teacher\s+models?)\b"
        ],
        "organizers": [
            r"\b(graphic\s+organizer|anchor\s+chart|t[\-\s]chart|venn|concept\s+map)\b"
        ],
        "gradual_release": [
            r"\bI\s+do[^\n]{0,30}we\s+do[^\n]{0,30}you\s+do\b",
            r"\bgradual\s+release\b",
        ],
        "chunking": [r"\b(chunk|partial\s+outline|guided\s+notes|cloze)\b"],
    },
    15: {
        "higher_bloom": [
            r"\b(analyze|evaluate|create|synthesi[sz]e|justify|argue|design|"
            r"hypothesi[sz]e|critique|compose|construct|formulate|appraise|defend)\b"
        ],
        "lower_bloom": [
            r"\b(remember|recall|list|name|identify|state|define|recognize|repeat)\b"
        ],
        "open_questions": [
            r"\b(how\s+(does|do|might|could)|why\s+(does|do|might|is|are)|"
            r"what\s+if|what\s+would\s+happen)\b"
        ],
        "compare_tasks": [r"\b(compare|contrast|differen(ce|tiate))\b"],
        "q_header": [
            r"\b(open[\-\s]?ended|analytical|reflective|exploratory|"
            r"interpret(ive|ation))\s+questions?\b"
        ],
        "argumentation": [r"\b(argue|justify|defend|claim.*evidence|CER\b)\b"],
    },
    16: {
        "pair": [r"\b(pair[s]?|partner[s]?|in\s+pairs|with\s+a\s+partner)\b"],
        "small_group": [
            r"\b(small\s+group[s]?|in\s+groups?|group\s+of\s+\d|group\s+work)\b"
        ],
        "whole_class": [
            r"\b(whole[\-\s]class|class\s+discussion|share\s+out|table\s+talk)\b"
        ],
        "elaborated": [
            r"\b(explain[^\n]{0,30}reasoning|extend[^\n]{0,30}answer|elaborate|"
            r"why\s+do\s+you\s+think)\b"
        ],
        "protocols": [
            r"\b(turn\s+and\s+talk|think[\-\s]?pair[\-\s]?share|jigsaw|"
            r"fishbowl|gallery\s+walk)\b"
        ],
    },
    17: {
        "rationale": [r"\bgroup(ing|ed)\s+(by|to|for|based\s+on)\b"],
        "multiple_types": [
            r"\b(whole[\-\s]class|small\s+group|pair[s]?|partner[s]?|individual)\b"
        ],
        "heterogeneous": [
            r"\b(mixed[\-\s]?(level|proficiency|ability)|heterogen|"
            r"with\s+(native\s+English\s+)?speakers)\b"
        ],
        "roles": [r"\b(role[s]?|recorder|reporter|facilitator|timekeeper)\b"],
    },
    18: {
        "wait_time": [r"\b(wait\s+time|think\s+time)\b"],
        "wait_duration": [
            r"\b(wait|think)\s+time[^\n]{0,40}\d+\s*(seconds?|minutes?)"
        ],
    },
    19: {
        "l1_use": [
            r"\b(L1|home\s+language|native\s+language|first\s+language|"
            r"primary\s+language)\b"
        ],
        "bilingual_peer": [
            r"\b(bilingual\s+(peer|aide|partner|buddy)|"
            r"translation\s+(partner|peer))\b"
        ],
        "translated_materials": [
            r"\b(translated|translation|"
            r"bilingual\s+(text|materials?|glossary|resources?))\b"
        ],
        "l1_brainstorm": [
            r"\b(discuss[^\n]{0,30}home\s+language|brainstorm[^\n]{0,30}L1|"
            r"use[^\n]{0,30}native\s+language\s+to)\b"
        ],
    },
    20: {
        "lab_equipment": [
            r"\b(beaker|flask|microscope|thermometer|balance|scale|test\s+tube|"
            r"petri\s+dish|graduated\s+cylinder|hand\s+lens|magnifier|magnet[s]?)\b"
        ],
        "construction": [
            r"\b(foam|clay|cardboard|paper|string|rope|tape|glue|popsicle|recycled)\b"
        ],
        "manipulatives": [
            r"\b(blocks?|cubes?|tiles?|counters?|cards?|chips|bead[s]?)\b"
        ],
        "kits": [r"\b(FOSS|STC|Amplify|Mystery\s+Science|kit)\b"],
        "realia": [
            r"\b(realia|specimen[s]?|live|actual\s+object[s]?|real\s+(thing|object))\b"
        ],
        "action_verbs": [
            r"\b(build|construct|measure|observe|dissect|manipulate|test)\b"
        ],
    },
    21: {
        "content_application": [
            r"\b(apply[^\n]{0,40}\b(concept|principle|idea|content)|"
            r"new\s+context|real[\-\s]world\s+(application|task)|"
            r"transfer|extend[^\n]{0,40}(idea|concept))\b"
        ],
        "language_application": [
            r"\b(use\s+(academic\s+language|new\s+vocabulary|sentence\s+frames?)|"
            r"oral\s+presentation|written\s+explanation|"
            r"convey[^\n]{0,40}(content|concept))\b"
        ],
    },
    22: {
        "reading": [r"\b(read(ing)?|article[s]?|text[s]?|passage|book[s]?)\b"],
        "writing": [
            r"\b(writ(e|ing)|journal|essay|notes?|paragraph|report|label)\b"
        ],
        "listening": [
            r"\b(listen(ing)?|video[s]?|audio|lecture|presentation|podcast)\b"
        ],
        "speaking": [
            r"\b(speak(ing)?|discuss(ion)?|share\s+out|present(ation)?|"
            r"oral|talk|conversation|debate)\b"
        ],
    },
    23: {
        "content_objective_header": [
            r"(?:content\s+objective|learning\s+(?:objective|target|goal))s?\s*[:\-]\s*"
            r"([^\n\.]{10,300})"
        ],
        "step_markers": [r"(?im)\bstep\s*\d+", r"(?m)^\s*\d+\.\s"],
    },
    24: {
        "language_objective_header": [
            r"language\s+objective[s]?\s*[:\-]\s*([^\n\.]{10,300})"
        ],
        "step_markers": [r"(?im)\bstep\s*\d+", r"(?m)^\s*\d+\.\s"],
    },
    25: {
        "active_verbs": [
            r"\bstudents?\s+(will|are|do|create|build|investigate|design|"
            r"explore|present|discuss|analyze|construct)\b"
        ],
        "pacing": [r"\b\d+\s*minutes?\b"],
        "multiple_phases": [
            r"\b(step\s*[2-9]|phase\s*[2-9]|then|next|after\s+that|finally)\b"
        ],
        "long_passive": [
            r"\bwatch\s+the\s+entire\s+video|silent\s+reading\s+for\s+\d+"
        ],
    },
    26: {
        "time_markers": [r"\b\d+\s*minutes?\b"],
        "total_duration": [
            r"\b(total\s+(time|duration)|class\s+period|\d+\s*minute\s+lesson)\b"
        ],
        "differentiation": [
            r"\b(fast\s+finishers?|early\s+finishers?|extension|additional\s+time)\b"
        ],
    },
    27: {
        "closing_vocab_review": [r"\b(vocabulary|key\s+(terms?|words?))\b"],
        "vocab_assessment": [
            r"\b(vocab(ulary)?\s+(test|quiz|assessment|check)|matching|"
            r"fill[\-\s]in[\-\s]the[\-\s]blank)\b"
        ],
        "word_wall_close": [
            r"\b(word\s+wall|anchor\s+chart|vocabulary\s+(wall|chart))\b"
        ],
        "repeated_use": [
            r"\b(repeat(ed)?\s+(exposure|use)|practice[^\n]{0,30}vocabulary|"
            r"use\s+new\s+(words?|terms?))\b"
        ],
    },
    28: {
        "closing_summary": [
            r"\b(summar(y|ize)|recap|review|wrap[\-\s]up|conclude|reflection)\b"
        ],
        "concept_check": [
            r"\b(check[s]?\s+for\s+understanding|exit\s+ticket|comprehension\s+check)\b"
        ],
        "objective_link": [r"\b(objective|goal|target)\b"],
        "student_articulation": [
            r"\bstudents?\s+(explain|share|present|articulate|reflect\s+on)\s+"
            r"(what|their|the)\b"
        ],
    },
    29: {
        "formative": [
            r"\b(feedback|formative\s+assessment|"
            r"check\s+for\s+understanding|monitoring)\b"
        ],
        "rubric": [r"\b(rubric|criteria|success\s+criteria)\b"],
        "peer_feedback": [
            r"\b(peer\s+(feedback|review|response)|partner\s+check)\b"
        ],
        "throughout": [
            r"\b(throughout|ongoing|continuous|frequent(ly)?)\s+"
            r"(feedback|check|monitor)\b"
        ],
    },
    30: {
        "multiple_moments": [
            r"\b(check[s]?\s+for\s+understanding|formative|exit\s+ticket|"
            r"quick\s+(check|write)|thumbs\s+(up|down))\b"
        ],
        "summative": [
            r"\b(summative|final\s+assessment|test|quiz|"
            r"end[\-\s]of[\-\s](unit|lesson))\b"
        ],
        "tied_to_objectives": [
            r"\bassess(ment)?[^\n]{0,80}(objective|goal|target)\b"
        ],
        "diverse_oral": [r"\boral|verbal\b"],
        "diverse_written": [r"\bwritten|writ(e|ing)\b"],
        "diverse_performance": [
            r"\bperformance|present(ation)?|demonstrat"
        ],
    },
}


def _snippet(text: str, span: tuple[int, int], window: int = 50) -> str:
    """Return a single-line excerpt of `text` around `span` with ellipses."""
    start = max(0, span[0] - window)
    end = min(len(text), span[1] + window)
    snippet = re.sub(r"\s+", " ", text[start:end]).strip()
    if start > 0:
        snippet = "…" + snippet
    if end < len(text):
        snippet = snippet + "…"
    return snippet


def extract_evidence(
    text: str,
    fnum: int,
    max_per_category: int = 2,
    window: int = 50,
) -> list[dict[str, str]]:
    """Find regex matches for feature `fnum` and return excerpts of `text`.

    Each item is ``{"category": str, "match": str, "snippet": str}``.
    De-duplicated by snippet so the same passage isn't shown multiple times.
    """
    if not text or fnum not in FEATURE_PATTERNS:
        return []
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for category, patterns in FEATURE_PATTERNS[fnum].items():
        cat_count = 0
        for pattern in patterns:
            if cat_count >= max_per_category:
                break
            for m in re.finditer(pattern, text, re.IGNORECASE):
                if cat_count >= max_per_category:
                    break
                snippet = _snippet(text, m.span(), window=window)
                key = (category, snippet)
                if key in seen:
                    continue
                seen.add(key)
                out.append(
                    {
                        "category": category,
                        "match": m.group(0).strip(),
                        "snippet": snippet,
                    }
                )
                cat_count += 1
    return out


def _yes_no(b: Any) -> str:
    return "yes" if b else "no"


def rationale(fnum: int, score: int, diag: dict[str, Any]) -> str:
    """Plain-English explanation of why feature `fnum` got `score` for this text.

    Translates the diagnostics dict into a short sentence so a human rater can
    see at a glance what drove the algorithm's decision.
    """
    if score == 0 and not any(
        diag.get(k) for k in ("hits", "distinct", "detected", "content_app",
                              "language_app", "multiple_moments")
    ):
        return "Score 0 — no matching indicators found in the activity text."

    bits: list[str] = []

    # Generic _generic_score-style diagnostics
    if "distinct" in diag:
        d = diag["distinct"]
        bits.append(
            f"{d} distinct indicator categor{'y' if d == 1 else 'ies'} matched"
        )
    if "hits" in diag:
        bits.append(f"{diag['hits']} total keyword/phrase hits")
    if "sec_cov" in diag:
        bits.append(
            f"present in {diag['sec_cov']} of 3 sections (opening / middle / closing)"
        )
    if diag.get("integration"):
        bits.append("the integration marker was found")
    if diag.get("cap_applied"):
        bits.append("score capped because the structural header is missing")
    if diag.get("partial_recovery_cap_applied"):
        bits.append(
            "partial-recovery cap applied (no explicit speech-modification protocol)"
        )
    if diag.get("only_video_cap"):
        bits.append("capped: only video evidence, no physical action")

    # Per-feature specifics where the diagnostics differ from the generic shape
    if fnum == 3:
        f3_bits = []
        if diag.get("has_grade"):
            f3_bits.append("explicit grade level stated")
        if diag.get("has_standard"):
            f3_bits.append("standards/curriculum reference present")
        fk = diag.get("fk")
        if fk is not None:
            f3_bits.append(f"Flesch–Kincaid readability ≈ grade {fk}")
        if f3_bits:
            bits.append("; ".join(f3_bits))
    elif fnum in (6, 22):
        skills = [
            label
            for key, label in (
                ("R", "Reading"),
                ("W", "Writing"),
                ("L", "Listening"),
                ("S", "Speaking"),
            )
            if diag.get(key)
        ]
        if skills:
            bits.append(f"language modalities present: {', '.join(skills)}")
        if "concept_tied" in diag and not diag["concept_tied"]:
            bits.append("activity not clearly tied to a content concept")
    elif fnum == 15:
        bits.append(
            f"higher-Bloom verbs={diag.get('higher_bloom', 0)}, "
            f"lower-Bloom verbs={diag.get('lower_bloom', 0)}, "
            f"open questions={diag.get('open_q', 0)}, "
            f"compare/contrast tasks={diag.get('compare', 0)}"
        )
        if diag.get("q_header"):
            bits.append("explicit higher-order question header found")
        if diag.get("argumentation"):
            bits.append("argumentation/CER pattern present")
    elif fnum == 18:
        if diag.get("detected"):
            bits.append(
                "explicit wait/think time mention"
                + (" with duration" if diag.get("duration") else " (no duration)")
            )
        else:
            bits.append("no wait-time language found")
    elif fnum == 21:
        ca, la = diag.get("content_app"), diag.get("language_app")
        if ca and la:
            bits.append("both content application AND language application present")
        elif ca:
            bits.append("content application present, but no language application")
        elif la:
            bits.append("language application present, but no content application")
    elif fnum in (23, 24):
        if "ratio" in diag:
            bits.append(
                f"TF-IDF alignment: {diag['aligned']}/{diag['n_steps']} "
                f"activity steps overlap with the objective "
                f"(ratio={diag['ratio']})"
            )
        elif "reason" in diag:
            bits.append(f"alignment skipped: {diag['reason']}")
    elif fnum == 25:
        bits.append(
            f"active-verb mentions={diag.get('active_verbs', 0)}, "
            f"pacing markers={diag.get('pacing_markers', 0)}, "
            f"multiple phases={_yes_no(diag.get('multiple_phases'))}, "
            f"long passive segments={_yes_no(diag.get('long_passive'))}"
        )
    elif fnum == 26:
        bits.append(
            f"{diag.get('time_markers', 0)} time-stamp markers; "
            f"total duration noted={_yes_no(diag.get('has_total'))}; "
            f"fast/early-finisher provisions="
            f"{_yes_no(diag.get('has_differentiation'))}"
        )
    elif fnum == 27:
        bits.append(
            f"{diag.get('distinct_close', 0)} vocabulary-review categories in the "
            f"closing section; repeated-use cue={_yes_no(diag.get('repeated_use'))}"
        )
    elif fnum == 28:
        bits.append(
            f"{diag.get('distinct_close', 0)} review categories in the closing "
            f"section; {diag.get('distinct_full', 0)} across the full text"
        )
    elif fnum == 30:
        bits.append(
            f"multiple checks-for-understanding="
            f"{_yes_no(diag.get('multiple_moments'))}; "
            f"formative+summative both present="
            f"{_yes_no(diag.get('formative') and diag.get('summative'))}; "
            f"assessment tied to objectives="
            f"{_yes_no(diag.get('tied_to_objectives'))}; "
            f"distinct assessment formats={diag.get('diverse_formats', 0)}"
        )

    return f"Score {score} — " + "; ".join(bits) + "."
