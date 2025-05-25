"""
LLM orchestration module for the Synai Prompt & Context Factory (SPCF).

This module handles the preparation of inputs for LLM interactions and 
processing of LLM outputs. It acts as an interface between the SPCF 
system and external LLM services.
"""

import os
import time
import xml.etree.ElementTree as ET
from typing import Optional
from utils import generate_hash
from prompt_manager import load_base_prompt, save_user_prompt


def prepare_designer_llm_input(context_string: str) -> str:
    """
    Prepare input for Synai Designer LLM by integrating context.
    
    This function loads the designer base prompt and integrates the user's
    aggregated context into the appropriate placeholder position.
    
    Args:
        context_string (str): The aggregated context from the user's context files
    
    Returns:
        str: The complete prompt ready to be sent to an LLM running 
             the Synai Designer persona
    """
    # Load designer base prompt
    designer_template = load_base_prompt('synai_designer.xml')
    
    # Replace the context placeholder with actual context
    # The placeholder {CONTEXT} is wrapped in XML comments for safety
    designer_input = designer_template.replace('{CONTEXT}', context_string)
    
    return designer_input


def validate_designer_output_xml(xml_string: str) -> bool:
    """
    Validate that the designer output is well-formed XML.
    
    Args:
        xml_string (str): The XML string to validate
    
    Returns:
        bool: True if valid XML, False otherwise
    """
    try:
        root = ET.fromstring(xml_string)
        # Basic validation - check if it's a synai element
        if root.tag != 'synai':
            return False
        # Could add more specific validation here
        return True
    except ET.ParseError:
        return False


def process_designer_llm_output(designer_llm_response_xml_str: str, 
                               user_id: str) -> str:
    """
    Process Synai Designer LLM output and save as seed prompt.
    
    This function validates the XML response from the designer LLM,
    generates a unique filename, and saves it as a seed prompt in
    the user's seeds directory.
    
    Args:
        designer_llm_response_xml_str (str): The XML response from the 
                                            Synai Designer LLM
        user_id (str): The unique identifier for the user
    
    Returns:
        str: The full path to the saved seed prompt file
    
    Raises:
        ValueError: If the XML response is invalid or malformed
    """
    # Validate XML response
    if not validate_designer_output_xml(designer_llm_response_xml_str):
        raise ValueError("Invalid XML response from Designer LLM. " +
                        "Response must be well-formed XML with root element 'synai'")
    
    # Parse XML to ensure it's well-formed and potentially extract metadata
    try:
        root = ET.fromstring(designer_llm_response_xml_str)
        
        # Optional: Add metadata about when this seed was generated
        # Find or create a metadata element
        metadata = root.find('metadata')
        if metadata is None:
            metadata = ET.SubElement(root, 'metadata')
        
        # Add generation timestamp
        ET.SubElement(metadata, 'generated_at').text = time.strftime('%Y-%m-%d %H:%M:%S')
        ET.SubElement(metadata, 'generated_by').text = 'synai_designer'
        ET.SubElement(metadata, 'user_id').text = user_id
        
        # Convert back to string with proper formatting
        designer_llm_response_xml_str = ET.tostring(root, encoding='unicode')
        
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse Designer LLM response: {str(e)}")
    
    # Generate unique filename for seed prompt
    timestamp = str(time.time())
    short_hash = generate_hash(user_id + timestamp, length=8)
    seed_filename = f"seed_prompt_{short_hash}_{int(float(timestamp))}.xml"
    
    # Save seed prompt to user's seeds directory
    seed_path = save_user_prompt(user_id, seed_filename, 
                                designer_llm_response_xml_str, 
                                subfolder="seeds")
    
    return seed_path


def extract_seed_data(seed_prompt_path: str) -> Optional[dict]:
    """
    Extract structured data from a seed prompt file.
    
    This is a utility function that can parse a seed prompt and extract
    any embedded JSON or structured data for analysis.
    
    Args:
        seed_prompt_path (str): Path to the seed prompt XML file
    
    Returns:
        dict or None: Extracted data if found, None otherwise
    """
    try:
        with open(seed_prompt_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        root = ET.fromstring(xml_content)
        
        # Look for various data containers
        # This is extensible based on how the designer structures its output
        data_element = root.find('.//data')
        if data_element is not None and data_element.text:
            import json
            try:
                return json.loads(data_element.text)
            except json.JSONDecodeError:
                pass
        
        # Could add more extraction logic here
        return None
        
    except Exception:
        return None