Feature: Inbound and Outbound Call Testing
  Demonstrates how to configure phone numbers and call direction in feature files

  Scenario: Inbound call - Customer calls support line
    Given a test case with id "inbound_support_call"
    And the persona is "Customer"
    And this is an inbound call
    And the to number is "+15551234567"
    And the from number is "+15559876543"
    And turn 1 where user says "Hi, I need help with my account"
    And the agent should respond with keywords "help, account, assist"
    And turn 2 where user says "I forgot my password"
    And the agent should respond with keywords "password, reset, email"
    When the test is executed
    Then the test should pass
    And 2 turns should be executed

  Scenario: Outbound call - Agent calls customer for appointment reminder
    Given a test case with id "outbound_appointment_reminder"
    And the persona is "Busy Professional"
    And this is an outbound call
    And the to number is "+15551234567"
    And the from number is "+15559876543"
    And turn 1 where user says "Hello?"
    And the agent should respond with keywords "appointment, reminder, tomorrow"
    And turn 2 where user says "Yes, I'll be there"
    And the agent should respond with keywords "confirmed, thank you"
    When the test is executed
    Then the test should pass
    And 2 turns should be executed

  Scenario: Outbound sales call - Alternative syntax
    Given a test case with id "outbound_sales_call"
    And the persona is "Interested Customer"
    And call direction is "outbound"
    And the call to number is "+15551111111"
    And the call from number is "+15552222222"
    And turn 1 where user says "Hello?"
    And the agent should respond with keywords "special, offer, discount"
    And turn 2 where user says "Tell me more"
    And the agent should respond with keywords "save, promotion, limited"
    When the test is executed
    Then the test should pass
    And 2 turns should be executed

  Scenario: Inbound emergency call
    Given a test case with id "inbound_emergency"
    And the persona is "Concerned Caller"
    And call direction is "inbound"
    And the destination number is "+15559999911"
    And the source number is "+15551234567"
    And turn 1 where user says "I need immediate assistance"
    And the agent should respond with keywords "emergency, help, immediately"
    When the test is executed
    Then the test should pass
    And 1 turns should be executed
