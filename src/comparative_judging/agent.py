"""
Decoy Judge LangGraph Agent

This agent implements comparative judging for remote viewing sessions using LangGraph.
It evaluates session data against a target and decoy images to determine which target
best matches the session information.

Key features:
- Single-pass ranking (no iterative elimination)
- Variable number of session files (images/PDFs)
- One target + description per message for clarity
- Verification node to ensure LLM reasoning matches target IDs
- Automatic retry on verification failure (max 2 attempts)
"""

import os
from typing import List, Optional, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, add_messages, END

# Load environment variables
load_dotenv()


# Pydantic models for input/output schemas
class SessionFile(BaseModel):
    """A session file (image or PDF) encoded in base64."""
    filename: str
    mime_type: str
    base64_content: str


class TargetImage(BaseModel):
    """Target or decoy image with metadata."""
    id: str
    description: str
    base64_image: str


class DecoyJudgeInput(BaseModel):
    """Input schema for the decoy judge agent."""
    session_files: List[SessionFile]
    target: TargetImage
    decoys: List[TargetImage]
    model_override: Optional[str] = "gpt-4o"


class RankedTarget(BaseModel):
    """A single ranked target result."""
    target_id: str = Field(..., description="The ID of the target")
    reasoning: str = Field(..., description="Specific reasoning for this ranking")
    rank: int = Field(..., ge=1, le=10, description="Ranking position (1 being the best match)")


class RankingResult(BaseModel):
    """Result from the ranking node."""
    overall_reasoning: str = Field(..., description="Overall analysis of the session content")
    top_matches: List[RankedTarget] = Field(..., min_length=1, max_length=10, description="Ranked targets")


class VerificationResult(BaseModel):
    """Result from the verification node."""
    is_valid: bool = Field(..., description="Whether the reasoning correctly references the target IDs")
    issues_found: Optional[str] = Field(None, description="Description of any issues found")


class DecoyJudgeOutput(BaseModel):
    """Final output schema for the decoy judge agent."""
    overall_reasoning: str
    top_matches: List[RankedTarget]
    correct_target_rank: Optional[int] = Field(None, description="Rank of the correct target if found")
    total_targets_ranked: int
    verification_passed: bool
    attempt_number: int


# Graph state
class DecoyJudgeState(TypedDict):
    """State for the decoy judge graph."""
    messages: Annotated[List[BaseMessage], add_messages]
    input_data: DecoyJudgeInput
    ranking_result: Optional[RankingResult]
    verification_result: Optional[VerificationResult]
    final_result: Optional[DecoyJudgeOutput]
    attempt_number: int


def ensure_pydantic_input(input_data) -> DecoyJudgeInput:
    """
    Ensure input_data is a proper Pydantic model, converting from dict if necessary.
    This handles LangGraph Studio serialization where Pydantic models become dicts.
    """
    if isinstance(input_data, DecoyJudgeInput):
        return input_data
    elif isinstance(input_data, dict):
        return DecoyJudgeInput(**input_data)
    else:
        raise ValueError(f"Unexpected input_data type: {type(input_data)}")


def create_ranking_messages(state: DecoyJudgeState) -> List[BaseMessage]:
    """Create messages for the ranking node with one target per message."""
    # Ensure we have a proper Pydantic model
    input_data = ensure_pydantic_input(state["input_data"])
    
    messages = []
    
    # Add system message
    system_prompt = """You are an expert Remote Viewing judge with deep knowledge of remote viewing methodology and evaluation criteria.

Remote Viewing is the practice of seeking impressions about distant or unseen targets through extrasensory perception. A remote viewing session typically involves:

1. **Perceptual Data**: Raw sensory impressions (visual, auditory, tactile, emotional, conceptual)
2. **Analytical Overlay (AOL)**: Conscious analytical interpretations that should be noted and bracketed
3. **Session Structure**: Often follows protocols like CRV (Controlled Remote Viewing) with stages
4. **Correspondence**: How well session data matches the actual target

What makes a good remote viewing session:
- **Accuracy**: Specific details that correspond to the target
- **Clarity**: Clear, detailed perceptual information
- **Minimal AOL**: Limited analytical overlay or properly managed when it occurs
- **Consistency**: Coherent themes and details throughout the session
- **Specificity**: Concrete details rather than vague generalities
- **Gestalt**: Overall impression that captures the essence of the target

Remote Viewing data may also include metaphors related to the target, or pieces of data not immediately visible in the target image.

Your task is to evaluate remote viewing session data against potential targets and determine which targets best correspond to the session's perceptual information. Focus on factual correspondences rather than symbolic interpretations.

IMPORTANT: When providing reasoning for each ranked target, make sure to clearly reference the target ID and describe why that specific target matches or doesn't match the session data."""

    messages.append(AIMessage(content=system_prompt))
    
    # Add session files description and content
    session_description = f"""Please analyze the following remote viewing session files and rank the potential targets based on how well they correspond to the session information.

**REMOTE VIEWING SESSION FILES:**
{chr(10).join([f"- {file.filename} ({file.mime_type})" for file in input_data.session_files])}

"""
    
    # Create multimodal content for session files
    session_content = [{"type": "text", "text": session_description}]
    
    for session_file in input_data.session_files:
        if session_file.mime_type.startswith('image/'):
            session_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{session_file.mime_type};base64,{session_file.base64_content}",
                    "detail": "high"
                }
            })
    
    messages.append(HumanMessage(content=session_content))
    
    # Add each target as a separate message with ID, description, and image
    all_targets = [input_data.target] + input_data.decoys
    
    for i, target in enumerate(all_targets, 1):
        target_content = [
            {
                "type": "text", 
                "text": f"**TARGET {i}:**\nID: {target.id}\nDescription: {target.description}"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{target.base64_image}",
                    "detail": "high"
                }
            }
        ]
        messages.append(HumanMessage(content=target_content))
    
    # Add final ranking instructions
    ranking_instructions = f"""Now please rank these {len(all_targets)} targets based on how well they match the remote viewing session data.

**INSTRUCTIONS:**
1. Examine all session files to identify key perceptual elements (visual details, shapes, colors, textures, emotions, conceptual impressions, handwritten notes, sketches, etc.)
2. Compare these elements against each target image and description
3. Look for both obvious visual correspondences and subtle conceptual/emotional connections
4. Rank the targets from best match (rank 1) to worst match
5. Provide specific reasoning for each ranked target that clearly references the target ID

Please provide your analysis in the specified JSON format."""
    
    messages.append(HumanMessage(content=ranking_instructions))
    
    return messages


def ranking_node(state: DecoyJudgeState) -> dict:
    """
    Node that performs the target ranking using structured output.
    """
    # Ensure we have a proper Pydantic model
    input_data = ensure_pydantic_input(state["input_data"])
    
    # Get the model from input or use default
    model = input_data.model_override or "gpt-4o"
    
    # Initialize the LLM with structured output
    llm = ChatOpenAI(
        model=model,
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    ).with_structured_output(RankingResult)
    
    # Create messages for ranking
    messages = create_ranking_messages(state)
    
    # Get ranking result
    ranking_result = llm.invoke(messages)
    
    return {
        "ranking_result": ranking_result,
        "messages": messages + [AIMessage(content=f"Ranking completed: {len(ranking_result.top_matches)} targets ranked")]
    }


def verification_node(state: DecoyJudgeState) -> dict:
    """
    Node that verifies the LLM's reasoning correctly references target IDs.
    """
    ranking_result = state["ranking_result"]
    
    # Ensure we have a proper Pydantic model
    input_data = ensure_pydantic_input(state["input_data"])
    
    if not ranking_result:
        return {"verification_result": VerificationResult(is_valid=False, issues_found="No ranking result found")}
    
    # Create verification prompt
    all_target_ids = [input_data.target.id] + [decoy.id for decoy in input_data.decoys]
    
    verification_prompt = f"""Please verify that the following ranking analysis correctly references the target IDs when discussing each target.

**AVAILABLE TARGET IDS:**
{chr(10).join([f"- {target_id}" for target_id in all_target_ids])}

**RANKING ANALYSIS TO VERIFY:**
Overall Reasoning: {ranking_result.overall_reasoning}

Top Matches:
{chr(10).join([f"Rank {match.rank}: Target ID '{match.target_id}' - {match.reasoning}" for match in ranking_result.top_matches])}

**VERIFICATION TASK:**
Check if:
1. Each ranked target uses a valid target ID from the available list
2. The reasoning for each target actually discusses that specific target (not a different one)
3. There are no obvious mix-ups where the reasoning describes one target but is attributed to another

Return true if the analysis is valid, false if there are issues."""

    # Initialize verification LLM
    llm = ChatOpenAI(
        model=input_data.model_override or "gpt-4o",
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    ).with_structured_output(VerificationResult)
    
    verification_result = llm.invoke([HumanMessage(content=verification_prompt)])
    
    return {
        "verification_result": verification_result,
        "messages": state["messages"] + [AIMessage(content=f"Verification completed: {verification_result.is_valid}")]
    }


def finalize_result_node(state: DecoyJudgeState) -> dict:
    """
    Node that creates the final output result.
    """
    ranking_result = state["ranking_result"]
    verification_result = state["verification_result"]
    attempt_number = state.get("attempt_number", 1)
    
    # Ensure we have a proper Pydantic model
    input_data = ensure_pydantic_input(state["input_data"])
    
    if not ranking_result:
        raise ValueError("No ranking result available for finalization")
    
    # Find the rank of the correct target
    correct_target_rank = None
    for match in ranking_result.top_matches:
        if match.target_id == input_data.target.id:
            correct_target_rank = match.rank
            break
    
    final_result = DecoyJudgeOutput(
        overall_reasoning=ranking_result.overall_reasoning,
        top_matches=ranking_result.top_matches,
        correct_target_rank=correct_target_rank,
        total_targets_ranked=len(ranking_result.top_matches),
        verification_passed=verification_result.is_valid if verification_result else False,
        attempt_number=attempt_number
    )
    
    return {
        "final_result": final_result,
        "messages": state["messages"] + [AIMessage(content="Final result generated")]
    }


def should_retry(state: DecoyJudgeState) -> str:
    """
    Conditional edge that determines if we should retry the ranking.
    """
    verification_result = state.get("verification_result")
    attempt_number = state.get("attempt_number", 1)
    
    # If verification passed or we've already tried twice, finalize
    if not verification_result or verification_result.is_valid or attempt_number >= 2:
        return "finalize"
    
    # Otherwise retry
    return "retry"


def retry_node(state: DecoyJudgeState) -> dict:
    """
    Node that increments attempt counter and clears previous results for retry.
    """
    return {
        "attempt_number": state.get("attempt_number", 1) + 1,
        "ranking_result": None,
        "verification_result": None,
        "messages": state["messages"] + [AIMessage(content="Retrying ranking due to verification failure")]
    }


def create_decoy_judge_graph():
    """Create and configure the Decoy Judge LangGraph application."""
    
    # Create the state graph
    workflow = StateGraph(DecoyJudgeState)
    
    # Add nodes
    workflow.add_node("ranking", ranking_node)
    workflow.add_node("verification", verification_node)
    workflow.add_node("finalize", finalize_result_node)
    workflow.add_node("retry", retry_node)
    
    # Set entry point
    workflow.set_entry_point("ranking")
    
    # Add edges
    workflow.add_edge("ranking", "verification")
    workflow.add_conditional_edges(
        "verification",
        should_retry,
        {
            "finalize": "finalize",
            "retry": "retry"
        }
    )
    workflow.add_edge("retry", "ranking")
    workflow.add_edge("finalize", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


# Create the graph instance for deployment
graph = create_decoy_judge_graph()


# Helper function to run the graph
async def judge_session_against_decoys(
    session_files: List[SessionFile],
    target: TargetImage,
    decoys: List[TargetImage],
    model_override: Optional[str] = None
) -> DecoyJudgeOutput:
    """
    Run the decoy judge graph with the provided inputs.
    
    Args:
        session_files: List of session files (images/PDFs) encoded in base64
        target: The correct target image with metadata
        decoys: List of decoy images with metadata
        model_override: Optional model override (defaults to gpt-4o)
    
    Returns:
        DecoyJudgeOutput with ranking results and verification status
    """
    input_data = DecoyJudgeInput(
        session_files=session_files,
        target=target,
        decoys=decoys,
        model_override=model_override
    )
    
    initial_state = DecoyJudgeState(
        messages=[],
        input_data=input_data,
        ranking_result=None,
        verification_result=None,
        final_result=None,
        attempt_number=1
    )
    
    result = await graph.ainvoke(initial_state)
    
    if not result.get("final_result"):
        raise ValueError("Graph execution failed to produce final result")
    
    return result["final_result"]


def create_initial_state(
    session_files: List[SessionFile],
    target: TargetImage,
    decoys: List[TargetImage],
    model_override: Optional[str] = None
) -> DecoyJudgeState:
    """
    Create the initial state for the decoy judge graph.
    Use this with `graph.ainvoke(state)` for LangGraph Studio visibility.
    
    Args:
        session_files: List of session files (images/PDFs) encoded in base64
        target: The correct target image with metadata
        decoys: List of decoy images with metadata
        model_override: Optional model override (defaults to gpt-4o)
    
    Returns:
        DecoyJudgeState ready for graph execution
    """
    input_data = DecoyJudgeInput(
        session_files=session_files,
        target=target,
        decoys=decoys,
        model_override=model_override
    )
    
    return DecoyJudgeState(
        messages=[],
        input_data=input_data,
        ranking_result=None,
        verification_result=None,
        final_result=None,
        attempt_number=1
    )

