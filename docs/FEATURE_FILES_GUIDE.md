# Feature Files Guide

This guide explains how to write and run Cucumber-style feature files for voice agent testing.

## Overview

Feature files allow you to write test cases in a natural, human-readable format using the Gherkin syntax. This is similar to the Cucumber framework used in other testing tools.

## File Structure

Feature files are stored in the `features/` directory with a `.feature` extension:

```
features/
├── billing_inquiry.feature
├── appointment_booking.feature
└── simple_examples.feature
```

## Feature File Syntax

A feature file consists of:

1. **Feature**: A high-level description of what is being tested
2. **Scenario**: A specific test case with Given-When-Then steps

### Example

```gherkin
Feature: Voice Agent Billing Inquiry
  As a customer service system
  I want to handle billing inquiries properly
  So that customers can understand their charges

  Scenario: Customer inquires about bill increase
    Given a test case with id "billing_inquiry_v1"
    And the persona is "Calm Customer"
    And turn 1 where user says "Hi, I noticed my bill jumped this month."
    And the agent should respond with keywords "account, review, details"
    And turn 2 where user says "Can you explain the extra charges?"
    And the agent should respond with keywords "overage, usage, explain"
    When the test is executed
    Then the test should pass
    And 3 turns should be executed
```

## Available Steps

### Setup Steps (Given/And)

- **`Given a test case with id "test_id"`**
  - Creates a new test case with a unique identifier
  
- **`And the persona is "Persona Name"`**
  - Sets the caller persona/character for the test
  
- **`And turn N where user says "user input"`**
  - Defines what the user says in turn N (where N is 1, 2, 3, etc.)
  
- **`And the agent should respond with keywords "keyword1, keyword2, keyword3"`**
  - Defines the keywords that must be present in the agent's response
  - Multiple keywords should be comma-separated
  
- **`And exact match is required`**
  - Optional: Requires the agent response to exactly match the keywords

### Execution Step (When)

- **`When the test is executed`**
  - Runs the simulation with the defined test case

### Verification Steps (Then/And)

- **`Then the test should pass`**
  - Verifies the overall test passed
  
- **`Then the test should fail`**
  - Verifies the overall test failed (for negative testing)
  
- **`And N turns should be executed`**
  - Verifies the number of conversation turns
  
- **`And turn N should pass`**
  - Verifies a specific turn passed validation
  
- **`And turn N should fail`**
  - Verifies a specific turn failed validation
  
- **`And the transcript should contain "text"`**
  - Verifies specific text appears in the conversation

## Running Feature Files

### Option 1: Using Behave (Recommended)

Run all feature files:
```bash
python scripts/run_features.py
```

Run a specific feature file:
```bash
behave features/billing_inquiry.feature
```

Run with specific tags:
```bash
behave --tags=@smoke
```

### Option 2: Load into Database and Use API

Load all feature files into the database:
```bash
python scripts/load_features.py
```

Then use the API to run tests:
```bash
curl -X POST http://localhost:8000/test/run \
  -H "Content-Type: application/json" \
  -d '{"test_id":"billing_inquiry_v1","provider":"twilio","mode":"simulation"}'
```

## Writing Your Own Feature Files

1. Create a new `.feature` file in the `features/` directory
2. Start with a Feature description
3. Add one or more Scenarios
4. For each scenario:
   - Give it a unique test_id
   - Set the persona
   - Define turns with user input and expected agent keywords
   - Add verification steps

### Example Template

```gherkin
Feature: [Feature Name]
  Brief description of what this feature tests

  Scenario: [Scenario Description]
    Given a test case with id "[unique_id]"
    And the persona is "[Persona Name]"
    And turn 1 where user says "[First thing user says]"
    And the agent should respond with keywords "[keyword1, keyword2]"
    And turn 2 where user says "[Second thing user says]"
    And the agent should respond with keywords "[keyword3, keyword4]"
    When the test is executed
    Then the test should pass
    And 2 turns should be executed
```

## Best Practices

1. **Use descriptive test IDs**: Make them meaningful and unique
2. **Keep scenarios focused**: Each scenario should test one specific flow
3. **Use realistic personas**: "Angry Customer", "Confused User", etc.
4. **Choose keywords carefully**: Pick words that uniquely identify correct responses
5. **Start simple**: Begin with 1-2 turns and add complexity as needed

## Integration with Existing Tests

Feature files work alongside existing Python tests. You can:

- Use both feature files and Python tests
- Convert existing test cases to feature files for better readability
- Generate feature files from database test cases

## Examples

See the `features/` directory for complete examples:
- `simple_examples.feature` - Basic examples to get started
- `billing_inquiry.feature` - Customer billing scenario
- `appointment_booking.feature` - Scheduling scenario
