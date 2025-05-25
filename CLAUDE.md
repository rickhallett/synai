# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Synai is an AI-powered psychological assessment and therapeutic support system based on Acceptance and Commitment Therapy (ACT) principles. It implements a sophisticated persona called "Synai" that serves as a specialized AI intake assistant for the "Art of Personal AI," designed to facilitate psychological flexibility and deeper self-understanding.

## Key Architecture Components

### Prompt System Architecture

The system uses a multi-stage prompt loading approach:

1. **Preloader (`synai-preloader.xml`)**: Instructs the LLM to passively accumulate context without processing
2. **Designer (`synai-designer.xml`)**: Processes pre-existing context to construct a full ACT case formulation JSON 
3. **Master Prompt (`seeds/ai.xml`)**: The full Synai persona with pre-loaded psychological data

### Core Data Structure

The system maintains an internal conceptual graph representing psychological concepts with:
- **Nodes**: Each concept (emotion, thought, belief, behavior, value, etc.) with attributes like ID, timestamp, ACT dimensions, Harris formulation area (A-H), weight, and links
- **Area Summary Stats**: Tracking node count and total weight for each of the 8 Harris formulation areas
- **Graph Metrics**: Breadth (areas covered) and depth (concepts per area) percentages

### ACT Framework Integration

The system maps all psychological content to:
- **ACT Hexaflex Dimensions**: experiential avoidance, cognitive fusion, present moment contact, etc.
- **Harris Formulation Areas (A-H)**:
  - A: Presenting Problem
  - B: Fusion/Barriers
  - C: Experiential Avoidance
  - D: Values
  - E: Committed Action
  - F: Self-as-Context
  - G: Present Moment Contact
  - H: Strengths/Resources

## Development Guidelines

### Prompt Modifications

When modifying prompts:
- Maintain consistency with ACT terminology and principles
- Preserve the JSON schema structure for data compatibility
- Test the complete loading sequence (preloader → designer → master prompt)

### Adding New Features

- New psychological concepts should map to existing ACT dimensions and Harris areas
- Maintain the conceptual graph structure for consistency
- Consider impact on breadth/depth metrics calculations

### Data Privacy Considerations

The pre-loaded data in `seeds/ai.xml` contains sensitive therapeutic content. Handle with appropriate confidentiality and security measures.