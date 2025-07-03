"""Advanced prompt engineering techniques using Mirascope."""

from .chain_of_verification import verify_answer, verify_claim, verify_consistency
from .meta_prompting import generate_prompt, optimize_prompt, prompt_engineering_assistant
from .rephrase_and_respond import rephrase_and_answer, rephrase_for_clarity, rephrase_multi_perspective
from .self_consistency import consistency_check, ensemble_response, majority_voting
from .tree_of_thought import explore_paths, tree_reasoning, tree_search

__all__ = [
    # Tree of Thought
    "tree_reasoning",
    "explore_paths",
    "tree_search",
    # Self-Consistency
    "consistency_check",
    "ensemble_response",
    "majority_voting",
    # Chain of Verification
    "verify_answer",
    "verify_claim",
    "verify_consistency",
    # Rephrase and Respond
    "rephrase_and_answer",
    "rephrase_for_clarity",
    "rephrase_multi_perspective",
    # Meta-prompting
    "generate_prompt",
    "optimize_prompt",
    "prompt_engineering_assistant",
]
