Feature: Advanced Voice Agent Testing Examples
  Demonstrates advanced testing scenarios and patterns

  @smoke
  Scenario: Basic smoke test for agent availability
    Given a test case with id "smoke_agent_available"
    And the persona is "Quick Tester"
    And turn 1 where user says "Hello"
    And the agent should respond with keywords "hello"
    When the test is executed
    Then the test should pass

  @regression
  Scenario: Multi-step customer support flow
    Given a test case with id "support_flow_regression"
    And the persona is "Frustrated Customer"
    And turn 1 where user says "I'm having trouble with my account"
    And the agent should respond with keywords "help, account"
    And turn 2 where user says "I can't log in"
    And the agent should respond with keywords "password, reset, email"
    And turn 3 where user says "Yes, please send a reset link"
    And the agent should respond with keywords "sent, check, email"
    When the test is executed
    Then the test should pass
    And 3 turns should be executed
    And turn 1 should pass
    And turn 2 should pass
    And turn 3 should pass

  @validation
  Scenario: Verify transcript content
    Given a test case with id "transcript_validation"
    And the persona is "Thorough Tester"
    And turn 1 where user says "What is your return policy?"
    And the agent should respond with keywords "return, policy, days"
    When the test is executed
    Then the test should pass
    And the transcript should contain "return"
    And the transcript should contain "policy"

  @edge-case
  Scenario: Single word responses
    Given a test case with id "minimal_responses"
    And the persona is "Brief User"
    And turn 1 where user says "Help"
    And the agent should respond with keywords "help"
    And turn 2 where user says "Thanks"
    And the agent should respond with keywords "welcome"
    When the test is executed
    Then the test should pass
    And 2 turns should be executed
