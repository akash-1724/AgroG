## MODIFIED Requirements

### Requirement: Conversational AI Assistance
The system SHALL provide a chat interface powered by an LLM backend to answer user queries about agriculture, crop issues, or farming practices.
The backend SHALL use configurable providers (Gemini/OpenAI) using keys defined in environment variables. If no keys are present, it SHALL gracefully fall back to a rule-based mock advisor without crashing.
The assistant response SHALL include: message content, safety disclaimers, and provider status.
The assistant SHALL reject requests requesting dangerous pesticide doses, illegal actions, or financial/medical guarantees with a pre-configured safety warning.

#### Scenario: Submitting a Farming Question
- **WHEN** a user sends a query to the chat assistant and API keys are configured
- **THEN** the system SHALL run the prompt against the AI provider and return the response along with a safety disclaimer and real-provider metadata

#### Scenario: AI Key Missing Fallback
- **WHEN** a user sends a query but no AI provider API keys are configured in the environment
- **THEN** the system SHALL return a fallback rule-based mock answer, clearly indicating demo/fallback state and safety guidelines

#### Scenario: Safe Rejection of Dangerous Prompts
- **WHEN** a user asks for dangerous chemical applications or financial guarantees
- **THEN** the system SHALL block the request and return a standard safety disclaimer advising expert consultation
