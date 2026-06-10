# AI Agriculture Assistant Specification

## Purpose
Initial definition of the AI Agriculture Assistant capability for AgroGuide.

## Requirements

### Requirement: Conversational AI Assistance
The system SHALL provide a chat interface powered by an LLM backend to answer user queries about agriculture, crop issues, or farming practices.

#### Scenario: Submitting a Farming Question
- **WHEN** a user sends a query to the chat assistant
- **THEN** the system SHALL stream or return a context-aware LLM response based on agricultural system prompts
