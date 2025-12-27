# Features Directory

This directory contains Cucumber-style feature files for voice agent testing.

## Structure

```
features/
├── steps/                          # Step definitions (Gherkin → Python)
│   └── voice_agent_steps.py       # All step implementations
├── simple_examples.feature         # Basic examples for learning
├── billing_inquiry.feature         # Customer billing scenario
├── appointment_booking.feature     # Appointment scheduling scenario
└── advanced_examples.feature       # Advanced patterns with tags
```

## Quick Start

Run all features:
```bash
python scripts/run_features.py
```

Run a specific feature:
```bash
behave features/simple_examples.feature
```

Run with tags:
```bash
behave features/ --tags=@smoke
```

## Available Feature Files

### simple_examples.feature
Basic examples to get started:
- Simple greeting interaction (1 turn)
- Multi-turn conversation (2 turns)

**Best for**: Learning the syntax and structure

### billing_inquiry.feature
Customer billing inquiry scenario:
- 3-turn conversation flow
- Keyword validation
- Step-by-step assertions

**Best for**: Understanding multi-turn interactions

### appointment_booking.feature
Service appointment booking:
- 3-turn scheduling flow
- Different persona demonstration

**Best for**: Seeing different scenarios in action

### advanced_examples.feature
Advanced testing patterns:
- Tag usage (@smoke, @regression, @validation, @edge-case)
- Transcript content validation
- Edge case handling

**Best for**: Learning advanced features and organization

## Creating Your Own Feature Files

1. Create a new `.feature` file in this directory
2. Follow the structure in `simple_examples.feature`
3. Run it with: `python scripts/run_features.py features/your_file.feature`

Example template:
```gherkin
Feature: My Feature
  Description of what you're testing

  Scenario: My test scenario
    Given a test case with id "my_test_id"
    And the persona is "My Persona"
    And turn 1 where user says "User input"
    And the agent should respond with keywords "expected, keywords"
    When the test is executed
    Then the test should pass
```

## Documentation

- **Quick Start**: [../docs/QUICKSTART_FEATURES.md](../docs/QUICKSTART_FEATURES.md)
- **Complete Guide**: [../docs/FEATURE_FILES_GUIDE.md](../docs/FEATURE_FILES_GUIDE.md)
- **Implementation Details**: [../docs/IMPLEMENTATION_SUMMARY.md](../docs/IMPLEMENTATION_SUMMARY.md)

## Tips

- Start with `simple_examples.feature` to learn the basics
- Use descriptive test IDs (they must be unique)
- Choose realistic personas
- Pick keywords that uniquely identify correct responses
- Use tags to organize your tests (@smoke, @regression, etc.)
- Run tests frequently as you develop
