Feature: Voice Agent Basic Conversation
  Simple example showing how to write voice agent test scenarios

  Scenario: Simple greeting interaction
    Given a test case with id "simple_greeting"
    And the persona is "Friendly User"
    And turn 1 where user says "Hello"
    And the agent should respond with keywords "hello, hi"
    When the test is executed
    Then the test should pass
    And 1 turns should be executed
    And the transcript should contain "hello"

  Scenario: Multi-turn conversation
    Given a test case with id "help_request"
    And the persona is "Helpful User"
    And turn 1 where user says "I need help"
    And the agent should respond with keywords "help, assist"
    And turn 2 where user says "Thank you"
    And the agent should respond with keywords "welcome"
    When the test is executed
    Then the test should pass
    And 2 turns should be executed
