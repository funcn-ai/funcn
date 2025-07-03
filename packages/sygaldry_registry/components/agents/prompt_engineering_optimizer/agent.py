from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator
from datetime import datetime
from enum import Enum
from mirascope import BaseDynamicConfig, llm, prompt_template
from pydantic import BaseModel, Field
from typing import Any, Optional


class OptimizationTechnique(str, Enum):
    """Prompt optimization techniques."""

    CHAIN_OF_THOUGHT = "chain_of_thought"
    FEW_SHOT = "few_shot"
    ZERO_SHOT = "zero_shot"
    ROLE_PLAYING = "role_playing"
    STEP_BY_STEP = "step_by_step"
    CONSTRAINT_BASED = "constraint_based"
    TEMPLATE_REFINEMENT = "template_refinement"
    CONTEXT_OPTIMIZATION = "context_optimization"
    OUTPUT_FORMATTING = "output_formatting"
    INSTRUCTION_CLARITY = "instruction_clarity"
    REASONING_FIRST = "reasoning_first"
    STRUCTURED_OUTPUT = "structured_output"
    NEGATIVE_EXAMPLES = "negative_examples"
    TASK_DECOMPOSITION = "task_decomposition"


class PromptIssue(str, Enum):
    """Common prompt issues to address."""

    AMBIGUOUS_INSTRUCTIONS = "ambiguous_instructions"
    MISSING_CONTEXT = "missing_context"
    POOR_EXAMPLES = "poor_examples"
    INCONSISTENT_OUTPUT = "inconsistent_output"
    LOW_ACCURACY = "low_accuracy"
    VERBOSE_OUTPUT = "verbose_output"
    HALLUCINATION = "hallucination"
    BIAS = "bias"
    POOR_FORMATTING = "poor_formatting"
    INCOMPLETE_RESPONSES = "incomplete_responses"
    LACK_OF_STRUCTURE = "lack_of_structure"
    UNCLEAR_EXPECTATIONS = "unclear_expectations"
    MISSING_CONSTRAINTS = "missing_constraints"
    TOKEN_INEFFICIENCY = "token_inefficiency"


class PromptAnalysis(BaseModel):
    """Analysis of a prompt's strengths and weaknesses."""

    clarity_score: float = Field(..., description="Clarity of instructions (0-1)")
    specificity_score: float = Field(..., description="Specificity of requirements (0-1)")
    context_adequacy: float = Field(..., description="Adequacy of context provided (0-1)")
    structure_quality: float = Field(..., description="Quality of prompt structure (0-1)")
    identified_issues: list[PromptIssue] = Field(..., description="Issues found in the prompt")
    strengths: list[str] = Field(..., description="Strengths of the current prompt")
    improvement_areas: list[str] = Field(..., description="Areas needing improvement")
    complexity_level: str = Field(..., description="Complexity level (simple/moderate/complex)")
    estimated_token_efficiency: float = Field(..., description="Token efficiency score (0-1)")
    overall_score: float = Field(..., description="Overall prompt quality score (0-1)")


class PromptVariant(BaseModel):
    """A variant of the original prompt with specific optimizations."""

    variant_id: str = Field(..., description="Unique identifier for the variant")
    variant_name: str = Field(..., description="Name of the variant")
    optimized_prompt: str = Field(..., description="The optimized prompt text")
    techniques_applied: list[OptimizationTechnique] = Field(..., description="Optimization techniques used")
    rationale: str = Field(..., description="Rationale for the optimizations")
    expected_improvements: list[str] = Field(..., description="Expected improvements")
    target_issues: list[PromptIssue] = Field(..., description="Issues this variant addresses")
    estimated_performance: float = Field(..., description="Expected performance score (0-1)")
    token_count: int = Field(..., description="Estimated token count")
    complexity_reduction: float = Field(..., description="Complexity reduction percentage")


class TestResult(BaseModel):
    """Result of testing a prompt variant."""

    variant_id: str = Field(..., description="ID of the tested variant")
    variant_name: str = Field(..., description="Name of the tested variant")
    test_input: str = Field(..., description="Input used for testing")
    output: str = Field(..., description="Generated output")
    quality_score: float = Field(..., description="Quality assessment (0-1)")
    accuracy_score: float = Field(..., description="Accuracy assessment (0-1)")
    consistency_score: float = Field(..., description="Consistency assessment (0-1)")
    efficiency_score: float = Field(..., description="Efficiency assessment (0-1)")
    response_time: float = Field(..., description="Response time in seconds")
    token_usage: int = Field(..., description="Tokens used in generation")
    issues_found: list[str] = Field(..., description="Issues identified in the output")
    strengths_found: list[str] = Field(..., description="Strengths identified in the output")
    meets_requirements: bool = Field(..., description="Whether output meets requirements")


class ABTestResult(BaseModel):
    """Result of A/B testing between variants."""

    variant_a_id: str = Field(..., description="ID of variant A")
    variant_b_id: str = Field(..., description="ID of variant B")
    winner: str = Field(..., description="ID of the winning variant")
    confidence_level: float = Field(..., description="Statistical confidence (0-1)")
    performance_delta: float = Field(..., description="Performance difference percentage")
    key_differences: list[str] = Field(..., description="Key differences in performance")
    recommendation: str = Field(..., description="Recommendation based on results")


class PromptOptimization(BaseModel):
    """Complete prompt optimization analysis."""

    original_prompt: str = Field(..., description="The original prompt")
    analysis: PromptAnalysis = Field(..., description="Analysis of the original prompt")
    variants: list[PromptVariant] = Field(..., description="Generated prompt variants")
    test_results: list[TestResult] = Field(..., description="Test results for variants")
    ab_test_results: list[ABTestResult] = Field(..., description="A/B test results")
    best_variant_id: str = Field(..., description="ID of the best performing variant")
    improvement_summary: str = Field(..., description="Summary of improvements achieved")
    recommendations: list[str] = Field(..., description="Additional recommendations")
    optimization_metrics: dict[str, float] = Field(..., description="Key optimization metrics")


class OptimizationResult(BaseModel):
    """Final optimization result with recommendations."""

    optimization: PromptOptimization
    final_prompt: str = Field(..., description="The final optimized prompt")
    performance_improvement: float = Field(..., description="Performance improvement percentage")
    key_changes: list[str] = Field(..., description="Key changes made to the prompt")
    usage_guidelines: list[str] = Field(..., description="Guidelines for using the optimized prompt")
    monitoring_suggestions: list[str] = Field(..., description="Suggestions for ongoing monitoring")
    version_history: list[dict[str, Any]] = Field(..., description="Version history of optimizations")
    next_steps: list[str] = Field(..., description="Recommended next steps for further optimization")


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=PromptAnalysis,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert prompt engineer and AI researcher with deep knowledge of
    prompt engineering best practices, cognitive science, and language model behavior.
    Your role is to analyze prompts for their effectiveness, clarity, and potential issues.

    Analyze prompts across these dimensions:
    1. Clarity: How clear and unambiguous are the instructions?
    2. Specificity: How specific are the requirements and expectations?
    3. Context: Is sufficient context provided for the task?
    4. Structure: Is the prompt well-organized and logical?
    5. Efficiency: How token-efficient is the prompt?
    6. Completeness: Does the prompt cover all necessary aspects?

    Common Issues to Look For:
    - Ambiguous or vague instructions
    - Missing context or background information
    - Poor or missing examples
    - Inconsistent formatting requirements
    - Potential for hallucination or bias
    - Overly verbose or inefficient structure
    - Lack of clear success criteria
    - Missing constraints or boundaries
    - Token inefficiency

    Scoring Guidelines:
    - 0.0-0.2: Critical issues, needs complete rewrite
    - 0.2-0.4: Major issues, significant improvements needed
    - 0.4-0.6: Moderate issues, several improvements recommended
    - 0.6-0.8: Minor issues, good with some refinements
    - 0.8-1.0: Excellent, minimal improvements needed

    USER:
    Analyze this prompt for effectiveness and identify areas for improvement:

    Prompt: {prompt}
    Task Context: {task_context}
    Target Audience: {target_audience}
    Success Criteria: {success_criteria}

    Provide a comprehensive analysis with specific scores and actionable insights.
    """
)
def analyze_prompt_effectiveness(
    prompt: str, task_context: str = "", target_audience: str = "", success_criteria: str = ""
) -> PromptAnalysis:
    """Analyze a prompt for effectiveness and identify issues."""
    ...


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=list[PromptVariant],
)
@prompt_template(
    """
    SYSTEM:
    You are an expert prompt optimization specialist with extensive experience
    in creating high-performance prompts for various AI applications.

    Optimization Techniques Available:
    - CHAIN_OF_THOUGHT: Add step-by-step reasoning
    - FEW_SHOT: Include relevant examples
    - ZERO_SHOT: Optimize for no-example scenarios
    - ROLE_PLAYING: Define specific roles or personas
    - STEP_BY_STEP: Break down complex tasks
    - CONSTRAINT_BASED: Add specific constraints and requirements
    - TEMPLATE_REFINEMENT: Improve structure and formatting
    - CONTEXT_OPTIMIZATION: Enhance context and background
    - OUTPUT_FORMATTING: Specify output format clearly
    - INSTRUCTION_CLARITY: Improve instruction clarity
    - REASONING_FIRST: Ask for reasoning before answer
    - STRUCTURED_OUTPUT: Request structured responses
    - NEGATIVE_EXAMPLES: Show what NOT to do
    - TASK_DECOMPOSITION: Break into subtasks

    For each variant:
    1. Apply 2-4 complementary techniques
    2. Address specific identified issues
    3. Maintain the core intent of the original prompt
    4. Provide clear rationale for changes
    5. Estimate expected performance improvements
    6. Ensure token efficiency
    7. Create diverse approaches for A/B testing

    USER:
    Create optimized variants of this prompt:

    Original Prompt: {original_prompt}
    Analysis Results: {analysis_results}
    Priority Issues: {priority_issues}
    Optimization Goals: {optimization_goals}

    Generate 4-6 distinct variants, each targeting different aspects of improvement.
    Ensure variants are sufficiently different for meaningful A/B testing.
    """
)
def generate_prompt_variants(
    original_prompt: str, analysis_results: PromptAnalysis, priority_issues: list[str], optimization_goals: str = ""
) -> BaseDynamicConfig:
    """Generate optimized prompt variants."""
    return {
        "computed_fields": {
            "analysis_results": analysis_results,
        }
    }


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=TestResult,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert prompt evaluation specialist with deep understanding
    of language model behavior and output quality assessment.

    Evaluation Criteria:
    1. Quality: Overall quality and usefulness of the output
    2. Accuracy: Factual correctness and relevance
    3. Consistency: Consistency with requirements and format
    4. Efficiency: Conciseness and token efficiency
    5. Completeness: Coverage of all required aspects

    For each test:
    - Simulate the prompt execution with the given input
    - Generate a realistic output based on the prompt
    - Evaluate the output across all criteria
    - Identify specific strengths and issues
    - Provide numerical scores (0-1 scale)
    - Assess whether requirements are met

    Consider:
    - Edge cases and potential failure modes
    - Consistency across different inputs
    - Token usage and efficiency
    - Response time implications
    - Practical usability

    USER:
    Test this prompt variant:

    Variant: {variant}
    Test Input: {test_input}
    Expected Output Type: {expected_output_type}
    Evaluation Context: {evaluation_context}
    Success Criteria: {success_criteria}

    Simulate execution and provide detailed evaluation results.
    """
)
def test_prompt_variant(
    variant: PromptVariant,
    test_input: str,
    expected_output_type: str = "",
    evaluation_context: str = "",
    success_criteria: str = "",
) -> BaseDynamicConfig:
    """Test a prompt variant and evaluate its performance."""
    return {
        "computed_fields": {
            "variant": variant,
        }
    }


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=ABTestResult,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert in A/B testing and statistical analysis for prompt optimization.
    Your role is to compare prompt variants and determine which performs better.

    Comparison Criteria:
    1. Overall performance scores
    2. Consistency across test cases
    3. Error rates and failure modes
    4. Token efficiency
    5. User satisfaction metrics
    6. Task completion rates

    Statistical Considerations:
    - Sample size and significance
    - Confidence intervals
    - Effect size
    - Practical significance vs statistical significance

    USER:
    Compare these two prompt variants:

    Variant A: {variant_a}
    Test Results A: {test_results_a}

    Variant B: {variant_b}
    Test Results B: {test_results_b}

    Evaluation Context: {evaluation_context}

    Determine the winner with statistical confidence and provide recommendations.
    """
)
def compare_variants_ab_test(
    variant_a: PromptVariant,
    test_results_a: list[TestResult],
    variant_b: PromptVariant,
    test_results_b: list[TestResult],
    evaluation_context: str = "",
) -> ABTestResult:
    """Perform A/B testing comparison between two variants."""
    pass


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=OptimizationResult,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert prompt optimization consultant specializing in
    delivering production-ready prompts with comprehensive documentation.

    Consider:
    1. Test results and performance metrics
    2. Trade-offs between different optimization approaches
    3. Practical implementation considerations
    4. Long-term maintenance and monitoring needs
    5. Usage guidelines and best practices
    6. Version control and iteration strategies

    Provide:
    - The final optimized prompt
    - Clear explanation of improvements
    - Performance improvement estimates
    - Implementation guidelines
    - Monitoring recommendations
    - Version history documentation
    - Next steps for continuous improvement

    USER:
    Synthesize the optimization results:

    Original Prompt: {original_prompt}
    Optimization Analysis: {optimization_analysis}
    Test Results: {test_results}
    A/B Test Results: {ab_test_results}
    Performance Goals: {performance_goals}

    Provide the final optimized prompt with comprehensive recommendations.
    """
)
def synthesize_optimization_results(
    original_prompt: str,
    optimization_analysis: PromptOptimization,
    test_results: list[TestResult],
    ab_test_results: list[ABTestResult],
    performance_goals: str = "",
) -> BaseDynamicConfig:
    """Synthesize optimization results into final recommendations."""
    return {
        "computed_fields": {
            "optimization_analysis": optimization_analysis,
            "test_results": test_results,
            "ab_test_results": ab_test_results,
        }
    }


async def run_variant_tests(
    variant: PromptVariant, test_inputs: list[str], expected_output_type: str, evaluation_context: str, success_criteria: str
) -> list[TestResult]:
    """Run tests for a single variant with multiple inputs."""
    test_results = []

    for test_input in test_inputs:
        # Simulate some processing time
        start_time = asyncio.get_event_loop().time()

        result = await test_prompt_variant(
            variant=variant,
            test_input=test_input,
            expected_output_type=expected_output_type,
            evaluation_context=evaluation_context,
            success_criteria=success_criteria,
        )

        # Add response time
        result.response_time = asyncio.get_event_loop().time() - start_time
        test_results.append(result)

    return test_results


async def prompt_engineering_optimizer(
    prompt: str,
    task_context: str = "",
    target_audience: str = "",
    success_criteria: str = "",
    test_inputs: list[str] = None,
    optimization_goals: str = "",
    expected_output_type: str = "text",
    max_variants: int = 5,
    enable_ab_testing: bool = True,
    llm_provider: str = "openai",
    model: str = "gpt-4o",
) -> OptimizationResult:
    """
    Optimize prompts using advanced prompt engineering techniques and testing.

    This agent analyzes prompts for effectiveness, generates optimized variants,
    tests them with sample inputs, performs A/B testing, and provides the best
    optimized version with comprehensive documentation.

    Args:
        prompt: The original prompt to optimize
        task_context: Context about the task the prompt is designed for
        target_audience: Target audience or use case
        success_criteria: Criteria for measuring success
        test_inputs: Sample inputs for testing variants
        optimization_goals: Specific optimization goals
        expected_output_type: Expected type of output (text, json, etc.)
        max_variants: Maximum number of variants to generate
        enable_ab_testing: Whether to perform A/B testing
        llm_provider: LLM provider to use
        model: Model to use for optimization

    Returns:
        OptimizationResult with the best optimized prompt and recommendations
    """

    if test_inputs is None:
        test_inputs = ["Sample test input for evaluation"]

    # Step 1: Analyze the original prompt
    print("🔍 Analyzing original prompt...")
    analysis = await analyze_prompt_effectiveness(
        prompt=prompt, task_context=task_context, target_audience=target_audience, success_criteria=success_criteria
    )
    print(f"📊 Analysis complete - Overall Score: {analysis.overall_score:.2f}, Issues: {len(analysis.identified_issues)}")

    # Step 2: Generate optimized variants
    print("🔧 Generating optimized variants...")
    priority_issues = [issue.value for issue in analysis.identified_issues[:3]]  # Top 3 issues
    variants = await generate_prompt_variants(
        original_prompt=prompt, analysis_results=analysis, priority_issues=priority_issues, optimization_goals=optimization_goals
    )

    # Limit variants to max_variants
    variants = variants[:max_variants]

    # Assign unique IDs to variants
    for i, variant in enumerate(variants):
        variant.variant_id = f"variant_{i + 1}"

    print(f"✨ Generated {len(variants)} optimized variants")

    # Step 3: Test all variants in parallel
    print("🧪 Testing prompt variants...")
    all_test_results = []

    # Run tests for all variants in parallel
    test_tasks = [
        run_variant_tests(variant, test_inputs, expected_output_type, task_context, success_criteria) for variant in variants
    ]

    variant_test_results = await asyncio.gather(*test_tasks)

    # Flatten results
    for results in variant_test_results:
        all_test_results.extend(results)

    print(f"📈 Completed {len(all_test_results)} tests")

    # Step 4: Perform A/B testing if enabled
    ab_test_results = []
    if enable_ab_testing and len(variants) > 1:
        print("🔬 Performing A/B testing...")

        # Compare top variants based on average performance
        variant_scores = {}
        for variant in variants:
            variant_results = [r for r in all_test_results if r.variant_id == variant.variant_id]
            avg_score = sum(r.quality_score for r in variant_results) / len(variant_results)
            variant_scores[variant.variant_id] = avg_score

        # Sort variants by score
        sorted_variants = sorted(variants, key=lambda v: variant_scores[v.variant_id], reverse=True)

        # A/B test top variants
        for i in range(min(3, len(sorted_variants) - 1)):  # Test top 3 pairs
            variant_a = sorted_variants[i]
            variant_b = sorted_variants[i + 1]

            results_a = [r for r in all_test_results if r.variant_id == variant_a.variant_id]
            results_b = [r for r in all_test_results if r.variant_id == variant_b.variant_id]

            ab_result = await compare_variants_ab_test(
                variant_a=variant_a,
                test_results_a=results_a,
                variant_b=variant_b,
                test_results_b=results_b,
                evaluation_context=task_context,
            )
            ab_test_results.append(ab_result)

        print(f"🔬 Completed {len(ab_test_results)} A/B tests")

    # Step 5: Determine best variant
    best_variant_id = max(
        variants, key=lambda v: sum(r.quality_score for r in all_test_results if r.variant_id == v.variant_id)
    ).variant_id

    # Step 6: Create optimization analysis
    optimization_metrics = {
        "avg_quality_improvement": 0.0,
        "token_efficiency_gain": 0.0,
        "consistency_improvement": 0.0,
        "accuracy_improvement": 0.0,
    }

    # Calculate metrics
    original_scores = analysis.overall_score
    best_variant_results = [r for r in all_test_results if r.variant_id == best_variant_id]
    if best_variant_results:
        avg_quality = sum(r.quality_score for r in best_variant_results) / len(best_variant_results)
        optimization_metrics["avg_quality_improvement"] = (avg_quality - original_scores) / original_scores * 100

    optimization_analysis = PromptOptimization(
        original_prompt=prompt,
        analysis=analysis,
        variants=variants,
        test_results=all_test_results,
        ab_test_results=ab_test_results,
        best_variant_id=best_variant_id,
        improvement_summary="Generated and tested optimized prompt variants with significant improvements",
        recommendations=[
            "Monitor performance in production",
            "A/B test with real users",
            "Iterate based on user feedback",
            "Track token usage and costs",
        ],
        optimization_metrics=optimization_metrics,
    )

    # Step 7: Synthesize final results
    print("🔄 Synthesizing optimization results...")
    final_result = await synthesize_optimization_results(
        original_prompt=prompt,
        optimization_analysis=optimization_analysis,
        test_results=all_test_results,
        ab_test_results=ab_test_results,
        performance_goals=optimization_goals,
    )

    print("✅ Prompt optimization complete!")
    return final_result


async def prompt_engineering_optimizer_stream(prompt: str, task_context: str = "", **kwargs) -> AsyncGenerator[str, None]:
    """Stream the prompt optimization process."""

    yield "🔧 Starting prompt optimization...\n\n"
    yield f"**Original Prompt:**\n```\n{prompt}\n```\n\n"

    # Perform optimization
    result = await prompt_engineering_optimizer(prompt, task_context, **kwargs)

    yield "## 📊 Analysis Results\n\n"
    analysis = result.optimization.analysis
    yield f"**Overall Score:** {analysis.overall_score:.2f}/1.0\n"
    yield f"**Clarity Score:** {analysis.clarity_score:.2f}/1.0\n"
    yield f"**Specificity Score:** {analysis.specificity_score:.2f}/1.0\n"
    yield f"**Context Adequacy:** {analysis.context_adequacy:.2f}/1.0\n"
    yield f"**Structure Quality:** {analysis.structure_quality:.2f}/1.0\n"
    yield f"**Token Efficiency:** {analysis.estimated_token_efficiency:.2f}/1.0\n\n"

    if analysis.identified_issues:
        yield "**Issues Identified:**\n"
        for issue in analysis.identified_issues:
            yield f"- {issue.value.replace('_', ' ').title()}\n"
        yield "\n"

    yield "## ✨ Optimized Variants Generated\n\n"
    for i, variant in enumerate(result.optimization.variants, 1):
        yield f"### Variant {i}: {variant.variant_name}\n"
        yield f"**Techniques:** {', '.join([t.value for t in variant.techniques_applied])}\n"
        yield f"**Expected Performance:** {variant.estimated_performance:.2f}/1.0\n"
        yield f"**Token Reduction:** {variant.complexity_reduction:.1f}%\n"
        yield f"**Rationale:** {variant.rationale}\n\n"

    if result.optimization.ab_test_results:
        yield "## 🔬 A/B Testing Results\n\n"
        for ab_result in result.optimization.ab_test_results:
            yield f"**{ab_result.variant_a_id} vs {ab_result.variant_b_id}**\n"
            yield f"- Winner: {ab_result.winner}\n"
            yield f"- Confidence: {ab_result.confidence_level:.2f}\n"
            yield f"- Performance Delta: {ab_result.performance_delta:.1f}%\n\n"

    yield "## 🏆 Final Optimized Prompt\n\n"
    yield f"**Performance Improvement:** +{result.performance_improvement:.1f}%\n\n"
    yield f"```\n{result.final_prompt}\n```\n\n"

    yield "## 🎯 Key Improvements\n\n"
    for change in result.key_changes:
        yield f"- {change}\n"

    yield "\n## 📋 Usage Guidelines\n\n"
    for guideline in result.usage_guidelines:
        yield f"- {guideline}\n"

    yield "\n## 🔄 Next Steps\n\n"
    for step in result.next_steps:
        yield f"- {step}\n"
