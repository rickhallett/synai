"""
Pipeline framework for the Synai Prompt & Context Factory (SPCF).

This module contains pre-defined pipelines that orchestrate sequences of
operations for common workflows in the SPCF system.
"""

from typing import Dict, Optional
from user_manager import create_user, get_user_paths
from prompt_manager import generate_user_assessment_prompt
from context_processor import get_user_context_string
from llm_orchestrator import prepare_designer_llm_input, process_designer_llm_output
from db_manager import log_operation


def pipeline_onboard_new_user_no_context(user_identifier: str, db_path: str) -> str:
    """
    Onboard a new user without context and generate assessment prompt.
    
    This pipeline:
    1. Creates a new user with the given identifier
    2. Generates an assessment prompt for the user
    3. Logs both operations to the database
    
    Args:
        user_identifier (str): A human-readable identifier for the user
        db_path (str): Path to the SQLite database file
    
    Returns:
        str: The generated user_id
    """
    # Step 1: Create user
    user_id = create_user(user_identifier)
    
    # Log user creation
    log_operation(
        db_path=db_path,
        user_id=user_id,
        operation_type="USER_CREATED",
        pipeline_name="onboard_new_user_no_context",
        input_params={"user_identifier": user_identifier},
        output_ref={"user_id": user_id}
    )
    
    # Step 2: Generate assessment prompt
    assessment_path = generate_user_assessment_prompt(user_id)
    
    # Log assessment prompt generation
    log_operation(
        db_path=db_path,
        user_id=user_id,
        operation_type="ASSESSMENT_PROMPT_GENERATED",
        pipeline_name="onboard_new_user_no_context",
        output_ref={"assessment_path": assessment_path}
    )
    
    return user_id


def pipeline_onboard_user_with_context_to_seed(user_identifier: str, 
                                               db_path: str) -> str:
    """
    Onboard a user with context and prepare for seed generation.
    
    This pipeline:
    1. Creates a new user (or could check if exists first)
    2. Aggregates context from the user's context directory
    3. Prepares input for the Synai Designer LLM
    4. Logs all operations with appropriate status
    
    Note: This pipeline prepares the designer input but does not execute
    the LLM call itself, as that's handled externally.
    
    Args:
        user_identifier (str): A human-readable identifier for the user
        db_path (str): Path to the SQLite database file
    
    Returns:
        str: The generated user_id
    """
    # Step 1: Create user (in production, might check if exists first)
    user_id = create_user(user_identifier)
    
    # Log user creation
    log_operation(
        db_path=db_path,
        user_id=user_id,
        operation_type="USER_CREATED",
        pipeline_name="onboard_user_with_context_to_seed",
        input_params={"user_identifier": user_identifier},
        output_ref={"user_id": user_id}
    )
    
    # Step 2: Get context string
    # Note: This assumes user has manually placed files in context directory
    try:
        context_string = get_user_context_string(user_id)
        context_length = len(context_string)
        
        # Log context aggregation
        log_operation(
            db_path=db_path,
            user_id=user_id,
            operation_type="CONTEXT_AGGREGATED",
            pipeline_name="onboard_user_with_context_to_seed",
            output_ref={"context_length": context_length}
        )
        
    except Exception as e:
        # Log failure
        log_operation(
            db_path=db_path,
            user_id=user_id,
            operation_type="CONTEXT_AGGREGATION_FAILED",
            pipeline_name="onboard_user_with_context_to_seed",
            status="FAILED",
            notes=str(e)
        )
        raise
    
    # Step 3: Prepare designer LLM input
    designer_input = prepare_designer_llm_input(context_string)
    
    # Log designer input preparation
    log_operation(
        db_path=db_path,
        user_id=user_id,
        operation_type="DESIGNER_INPUT_PREPARED",
        pipeline_name="onboard_user_with_context_to_seed",
        status="PENDING_LLM",
        output_ref={
            "designer_input_length": len(designer_input),
            "context_included": context_length > 0
        },
        notes="Ready for external LLM processing"
    )
    
    # Note: The actual LLM call happens externally
    # The designer_input would be passed to the LLM service
    
    return user_id


def pipeline_process_seed_from_designer_output(user_id: str, 
                                              designer_llm_response_xml_str: str, 
                                              db_path: str) -> str:
    """
    Process Designer LLM output and save as seed prompt.
    
    This pipeline:
    1. Processes the designer LLM response
    2. Saves it as a seed prompt
    3. Logs the operation
    
    Args:
        user_id (str): The unique identifier for the user
        designer_llm_response_xml_str (str): The XML response from Synai Designer
        db_path (str): Path to the SQLite database file
    
    Returns:
        str: The path to the saved seed prompt file
    """
    try:
        # Process designer output
        seed_path = process_designer_llm_output(designer_llm_response_xml_str, user_id)
        
        # Log successful seed generation
        log_operation(
            db_path=db_path,
            user_id=user_id,
            operation_type="SEED_PROMPT_GENERATED",
            pipeline_name="process_seed_from_designer_output",
            input_params={
                "designer_response_length": len(designer_llm_response_xml_str)
            },
            output_ref={"seed_path": seed_path},
            status="SUCCESS"
        )
        
        return seed_path
        
    except Exception as e:
        # Log failure
        log_operation(
            db_path=db_path,
            user_id=user_id,
            operation_type="SEED_GENERATION_FAILED",
            pipeline_name="process_seed_from_designer_output",
            input_params={
                "designer_response_length": len(designer_llm_response_xml_str)
            },
            status="FAILED",
            notes=f"Error: {str(e)}"
        )
        raise


def pipeline_full_user_onboarding_with_context(user_identifier: str,
                                               context_files: Dict[str, str],
                                               designer_llm_response: str,
                                               db_path: str) -> Dict[str, str]:
    """
    Complete end-to-end user onboarding with context and seed generation.
    
    This is a convenience pipeline that combines all steps, useful for
    testing or when you have all inputs ready.
    
    Args:
        user_identifier (str): A human-readable identifier for the user
        context_files (dict): Dictionary of filename: content for context files
        designer_llm_response (str): The designer LLM response (for testing)
        db_path (str): Path to the SQLite database file
    
    Returns:
        dict: Contains user_id, assessment_path, and seed_path
    """
    # Create user
    user_id = create_user(user_identifier)
    
    # Log user creation
    log_operation(
        db_path=db_path,
        user_id=user_id,
        operation_type="USER_CREATED",
        pipeline_name="full_user_onboarding_with_context",
        input_params={"user_identifier": user_identifier},
        output_ref={"user_id": user_id}
    )
    
    # Generate assessment prompt
    assessment_path = generate_user_assessment_prompt(user_id)
    
    # Log assessment generation
    log_operation(
        db_path=db_path,
        user_id=user_id,
        operation_type="ASSESSMENT_PROMPT_GENERATED",
        pipeline_name="full_user_onboarding_with_context",
        output_ref={"assessment_path": assessment_path}
    )
    
    # Write context files
    user_paths = get_user_paths(user_id)
    from utils import write_file
    import os
    
    for filename, content in context_files.items():
        file_path = os.path.join(user_paths['context'], filename)
        write_file(file_path, content)
    
    # Get aggregated context
    context_string = get_user_context_string(user_id)
    
    # Log context aggregation
    log_operation(
        db_path=db_path,
        user_id=user_id,
        operation_type="CONTEXT_AGGREGATED",
        pipeline_name="full_user_onboarding_with_context",
        output_ref={
            "context_length": len(context_string),
            "files_count": len(context_files)
        }
    )
    
    # Prepare designer input
    designer_input = prepare_designer_llm_input(context_string)
    
    # Log designer preparation
    log_operation(
        db_path=db_path,
        user_id=user_id,
        operation_type="DESIGNER_INPUT_PREPARED",
        pipeline_name="full_user_onboarding_with_context",
        output_ref={"designer_input_length": len(designer_input)}
    )
    
    # Process designer output (using provided response)
    seed_path = process_designer_llm_output(designer_llm_response, user_id)
    
    # Log seed generation
    log_operation(
        db_path=db_path,
        user_id=user_id,
        operation_type="SEED_PROMPT_GENERATED",
        pipeline_name="full_user_onboarding_with_context",
        output_ref={"seed_path": seed_path}
    )
    
    return {
        "user_id": user_id,
        "assessment_path": assessment_path,
        "seed_path": seed_path
    }