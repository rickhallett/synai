"""
Test file for llm_orchestrator.py module.
Run this to verify LLM orchestration functions work correctly.
"""

import os
import tempfile
import xml.etree.ElementTree as ET
from llm_orchestrator import (
    prepare_designer_llm_input, 
    validate_designer_output_xml,
    process_designer_llm_output,
    extract_seed_data
)
from user_manager import create_user
from utils import write_file, ensure_dir_exists, read_file


def test_prepare_designer_llm_input():
    """Test the prepare_designer_llm_input function."""
    print("Testing prepare_designer_llm_input...")
    
    # Test with sample context
    test_context = """### Context from background.txt ###
I have been experiencing anxiety in social situations.
My values include family, creativity, and personal growth.

### Context from goals.txt ###
I want to develop better coping strategies for anxiety.
I want to align my actions with my values."""
    
    # Prepare designer input
    designer_input = prepare_designer_llm_input(test_context)
    
    # Verify the output contains expected elements
    assert "<?xml version=" in designer_input, "Should contain XML declaration"
    assert "<mode>designer</mode>" in designer_input, "Should contain designer mode"
    assert test_context in designer_input, "Should contain the provided context"
    assert "{CONTEXT}" not in designer_input, "Context placeholder should be replaced"
    
    # Verify it's valid XML
    try:
        ET.fromstring(designer_input)
    except ET.ParseError:
        assert False, "Output should be valid XML"
    
    print("✓ prepare_designer_llm_input tests passed")


def test_validate_designer_output_xml():
    """Test the validate_designer_output_xml function."""
    print("Testing validate_designer_output_xml...")
    
    # Test valid XML with synai root
    valid_xml = """<?xml version="1.0" encoding="UTF-8"?>
<synai>
    <mode>seed</mode>
    <data>{"test": "data"}</data>
</synai>"""
    assert validate_designer_output_xml(valid_xml) == True, "Valid XML should pass"
    
    # Test invalid XML
    invalid_xml = """<synai>
    <unclosed_tag>
</synai>"""
    assert validate_designer_output_xml(invalid_xml) == False, "Invalid XML should fail"
    
    # Test XML with wrong root element
    wrong_root = """<?xml version="1.0" encoding="UTF-8"?>
<notsynai>
    <data>test</data>
</notsynai>"""
    assert validate_designer_output_xml(wrong_root) == False, "Wrong root element should fail"
    
    # Test non-XML content
    not_xml = "This is not XML at all"
    assert validate_designer_output_xml(not_xml) == False, "Non-XML should fail"
    
    print("✓ validate_designer_output_xml tests passed")


def test_process_designer_llm_output():
    """Test the process_designer_llm_output function."""
    print("Testing process_designer_llm_output...")
    
    # Save current directory
    original_dir = os.getcwd()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Set up required directory structure
        ensure_dir_exists('data/users')
        
        # Create a test user
        user_id = create_user("test_designer_output_user")
        
        # Test with valid designer output
        valid_designer_output = """<?xml version="1.0" encoding="UTF-8"?>
<synai>
    <mode>seed</mode>
    <version>1.0</version>
    <preloaded_data>
        <concepts>
            <concept>
                <id>anxiety_social_1</id>
                <type>emotion</type>
                <content>Anxiety in social situations</content>
                <act_dimension>experiential_avoidance</act_dimension>
                <harris_area>C</harris_area>
                <weight>0.8</weight>
            </concept>
        </concepts>
    </preloaded_data>
</synai>"""
        
        # Process the output
        seed_path = process_designer_llm_output(valid_designer_output, user_id)
        
        # Verify file was created
        assert os.path.exists(seed_path), "Seed file should be created"
        assert "seeds/" in seed_path, "Seed should be in seeds directory"
        assert seed_path.endswith(".xml"), "Seed should be XML file"
        
        # Verify content includes metadata
        saved_content = read_file(seed_path)
        root = ET.fromstring(saved_content)
        metadata = root.find('metadata')
        assert metadata is not None, "Metadata should be added"
        assert metadata.find('user_id').text == user_id, "User ID should be in metadata"
        assert metadata.find('generated_by').text == 'synai_designer', "Generator should be recorded"
        
        # Test with invalid XML
        try:
            process_designer_llm_output("<invalid>xml", user_id)
            assert False, "Should raise ValueError for invalid XML"
        except ValueError as e:
            assert "Invalid XML response" in str(e)
        
        os.chdir(original_dir)
    
    print("✓ process_designer_llm_output tests passed")


def test_extract_seed_data():
    """Test the extract_seed_data function."""
    print("Testing extract_seed_data...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test seed file with embedded JSON data
        seed_with_data = """<?xml version="1.0" encoding="UTF-8"?>
<synai>
    <mode>seed</mode>
    <data>{"concepts": [{"id": "test1", "type": "emotion"}], "metrics": {"total": 1}}</data>
</synai>"""
        
        seed_path = os.path.join(tmpdir, "test_seed.xml")
        write_file(seed_path, seed_with_data)
        
        # Test extraction
        data = extract_seed_data(seed_path)
        assert data is not None, "Should extract data"
        assert "concepts" in data, "Should have concepts"
        assert len(data["concepts"]) == 1, "Should have one concept"
        assert data["concepts"][0]["id"] == "test1", "Should extract correct data"
        
        # Test seed without data element
        seed_no_data = """<?xml version="1.0" encoding="UTF-8"?>
<synai>
    <mode>seed</mode>
    <content>No structured data here</content>
</synai>"""
        
        no_data_path = os.path.join(tmpdir, "no_data_seed.xml")
        write_file(no_data_path, seed_no_data)
        
        data = extract_seed_data(no_data_path)
        assert data is None, "Should return None when no data element"
        
        # Test non-existent file
        data = extract_seed_data(os.path.join(tmpdir, "nonexistent.xml"))
        assert data is None, "Should return None for non-existent file"
    
    print("✓ extract_seed_data tests passed")


def test_integration():
    """Test integration of LLM orchestration functions."""
    print("Testing LLM orchestration integration...")
    
    # Use actual project directory
    user_id = create_user("integration_test_llm_user")
    
    # Prepare realistic context
    context = """### Context from therapy_background.txt ###
-------------------------------------------
I've been working with ACT principles for the past few months.
My main struggle is with anxiety, particularly in work situations.
I tend to avoid difficult conversations and procrastinate on challenging tasks.

### Context from values_exploration.txt ###
-------------------------------------------
Through values clarification exercises, I've identified:
- Family: Being present and supportive for my loved ones
- Growth: Continuous learning and self-improvement
- Authenticity: Being true to myself and my beliefs"""
    
    # Prepare designer input
    designer_input = prepare_designer_llm_input(context)
    
    # Verify input is well-formed
    assert len(designer_input) > 1000, "Designer input should be substantial"
    assert "ACT principles" in designer_input, "Should contain context"
    assert "Synai Designer" in designer_input, "Should contain designer instructions"
    
    # Simulate designer output
    simulated_designer_output = """<?xml version="1.0" encoding="UTF-8"?>
<synai>
    <mode>seed</mode>
    <version>1.0</version>
    <preloaded_data>
        <psychological_profile>
            <concepts>
                <concept>
                    <id>work_anxiety_001</id>
                    <type>emotion</type>
                    <content>Anxiety in work situations</content>
                    <act_dimension>experiential_avoidance</act_dimension>
                    <harris_area>C</harris_area>
                    <weight>0.85</weight>
                    <links>["avoidance_pattern_001", "procrastination_001"]</links>
                </concept>
                <concept>
                    <id>avoidance_pattern_001</id>
                    <type>behavior</type>
                    <content>Avoiding difficult conversations</content>
                    <act_dimension>experiential_avoidance</act_dimension>
                    <harris_area>C</harris_area>
                    <weight>0.75</weight>
                </concept>
            </concepts>
            <values>
                <value>
                    <id>family_value_001</id>
                    <content>Being present and supportive for loved ones</content>
                    <harris_area>D</harris_area>
                    <importance>0.9</importance>
                </value>
            </values>
        </psychological_profile>
    </preloaded_data>
    <data>{"summary": "User shows patterns of experiential avoidance in work contexts"}</data>
</synai>"""
    
    # Process designer output
    seed_path = process_designer_llm_output(simulated_designer_output, user_id)
    
    # Verify seed was created correctly
    assert os.path.exists(seed_path), "Seed file should exist"
    
    # Extract and verify data
    extracted_data = extract_seed_data(seed_path)
    assert extracted_data is not None, "Should extract data"
    assert "summary" in extracted_data, "Should have summary"
    
    print("✓ Integration tests passed")


def main():
    """Run all tests."""
    print("Running llm_orchestrator.py tests...\n")
    
    test_prepare_designer_llm_input()
    test_validate_designer_output_xml()
    test_process_designer_llm_output()
    test_extract_seed_data()
    test_integration()
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()