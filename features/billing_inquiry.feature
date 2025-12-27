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
    And turn 3 where user says "Thanks, what are my options to lower it?"
    And the agent should respond with keywords "discount, plan, offer"
    When the test is executed
    Then the test should pass
    And 3 turns should be executed
    And turn 1 should pass
    And turn 2 should pass
    And turn 3 should pass
