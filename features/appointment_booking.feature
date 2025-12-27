Feature: Voice Agent Appointment Booking
  As a scheduling system
  I want to book appointments for customers
  So that they can schedule service visits

  Scenario: Customer books a morning service appointment
    Given a test case with id "appointment_booking_v1"
    And the persona is "Impatient Caller"
    And turn 1 where user says "I need to schedule a service visit."
    And the agent should respond with keywords "availability, date"
    And turn 2 where user says "Morning slots only, please."
    And the agent should respond with keywords "morning, confirm"
    And turn 3 where user says "Send me a confirmation text."
    And the agent should respond with keywords "text, confirmation"
    When the test is executed
    Then the test should pass
    And 3 turns should be executed
