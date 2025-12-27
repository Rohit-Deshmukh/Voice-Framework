# Call Direction Configuration Guide

This guide explains how to configure phone numbers and call direction in feature files for testing both inbound and outbound call scenarios.

## Overview

The Voice Framework supports two types of call scenarios:

1. **Inbound Calls**: User calls the AI agent (e.g., customer calling support line)
2. **Outbound Calls**: AI agent calls the user (e.g., appointment reminders, sales calls)

## Feature File Syntax

### Specifying Call Direction

You can specify the call direction in several ways:

#### Method 1: Using explicit direction flag
```gherkin
And call direction is "inbound"
And call direction is "outbound"
```

#### Method 2: Using shorthand notation
```gherkin
And this is an inbound call
And this is an outbound call
```

### Specifying Phone Numbers

Phone numbers can be specified using multiple syntaxes:

#### Standard syntax
```gherkin
And the to number is "+15551234567"
And the from number is "+15559876543"
```

#### Alternative syntax with "call" prefix
```gherkin
And the call to number is "+15551234567"
And the call from number is "+15559876543"
```

#### Semantic aliases
```gherkin
And the destination number is "+15551234567"
And the source number is "+15559876543"
```

## Complete Examples

### Example 1: Inbound Support Call

```gherkin
Scenario: Customer calls support line
  Given a test case with id "inbound_support"
  And the persona is "Frustrated Customer"
  And this is an inbound call
  And the to number is "+15551234567"
  And the from number is "+15559876543"
  And turn 1 where user says "I need help with my account"
  And the agent should respond with keywords "help, account, assist"
  When the test is executed
  Then the test should pass
```

**Explanation**:
- **Call Direction**: Inbound (customer calls agent)
- **To Number**: Agent's phone number (+15551234567)
- **From Number**: Customer's phone number (+15559876543)

### Example 2: Outbound Appointment Reminder

```gherkin
Scenario: Agent calls customer for appointment
  Given a test case with id "outbound_reminder"
  And the persona is "Busy Professional"
  And this is an outbound call
  And the to number is "+15551234567"
  And the from number is "+15559876543"
  And turn 1 where user says "Hello?"
  And the agent should respond with keywords "appointment, reminder"
  When the test is executed
  Then the test should pass
```

**Explanation**:
- **Call Direction**: Outbound (agent calls customer)
- **To Number**: Customer's phone number (+15551234567)
- **From Number**: Agent's/System's phone number (+15559876543)

## Phone Number Precedence

When running tests via the API, phone numbers can be specified in three places with the following precedence:

1. **API Request** (highest priority) - Numbers in the POST /test/run payload
2. **Feature File** - Numbers specified in the test case
3. **Environment Config** (lowest priority) - Default numbers from settings

Example API request that overrides feature file numbers:
```bash
curl -X POST http://localhost:8000/test/run \
  -H "Content-Type: application/json" \
  -d '{
    "test_id": "inbound_support",
    "provider": "twilio",
    "mode": "live",
    "to_number": "+15559999999",
    "from_number": "+15558888888"
  }'
```

## Call Direction Semantics

### Inbound Call (Default)
- **Scenario**: User initiates the call to the agent
- **To Number**: Agent's phone number (the number being called)
- **From Number**: User's phone number (the caller)
- **Use Cases**: 
  - Customer support hotlines
  - Help desk lines
  - Emergency services
  - Information lines

### Outbound Call
- **Scenario**: Agent initiates the call to the user
- **To Number**: User's phone number (the recipient)
- **From Number**: Agent's/System's phone number (the caller)
- **Use Cases**:
  - Appointment reminders
  - Follow-up calls
  - Sales/marketing calls
  - Survey calls
  - Delivery notifications

## Default Behavior

If call direction is not specified in the feature file:
- **Default Direction**: `inbound`
- **Default Numbers**: `null` (must be provided via API or environment)

## Integration with API

The call direction is automatically passed to the telephony provider as metadata:

```python
{
  "call_direction": "inbound",  # or "outbound"
  "to_number": "+15551234567",
  "from_number": "+15559876543"
}
```

This allows telephony providers to:
- Set up appropriate call flows
- Configure IVR systems differently
- Apply different call handling logic
- Track metrics by call direction

## Testing Strategies

### Test Both Directions

For comprehensive testing, create test cases for both directions:

```gherkin
Feature: Complete Call Coverage
  
  @inbound
  Scenario: Test inbound customer support
    Given a test case with id "support_inbound"
    And this is an inbound call
    # ... rest of test
  
  @outbound
  Scenario: Test outbound reminder system
    Given a test case with id "reminder_outbound"
    And this is an outbound call
    # ... rest of test
```

### Use Tags for Organization

Organize your tests using tags:
- `@inbound` - Tests for inbound calls
- `@outbound` - Tests for outbound calls
- `@emergency` - Emergency call scenarios
- `@sales` - Sales call scenarios

## Limitations

1. Phone numbers must be in E.164 format (e.g., +15551234567)
2. Call direction affects metadata but not test execution logic in simulation mode
3. In live mode, the telephony provider must support both inbound and outbound calling

## Simulation vs Live Mode

### Simulation Mode
- Call direction is stored but doesn't affect execution
- Phone numbers are optional
- Tests run instantly without real calls

### Live Mode
- Call direction determines call setup
- Phone numbers are required
- Real telephony provider is used
- Actual calls are made

## Troubleshooting

### Error: "to_number is required for live mode"
**Solution**: Add phone number to feature file or API request:
```gherkin
And the to number is "+15551234567"
```

### Numbers not being used
**Check**:
1. Feature file has correct syntax
2. API request isn't overriding
3. Numbers are in E.164 format

### Call direction not working
**Verify**:
1. Syntax: `And this is an inbound call` or `And call direction is "inbound"`
2. Case sensitivity: use lowercase "inbound" or "outbound"
3. Quotation marks: optional for shorthand, required for explicit

## See Also

- [Feature Files Guide](FEATURE_FILES_GUIDE.md) - Complete feature file syntax
- [Quick Start](QUICKSTART_FEATURES.md) - Getting started with feature files
- [API Documentation](../README.md#api-surface) - API endpoint details
