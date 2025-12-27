# Quick Start: Running Feature Files

This quick start guide shows you how to run voice agent tests using Cucumber-style feature files.

## Installation

1. **Install the base dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install feature file support:**
   ```bash
   pip install -r requirements-features.txt
   ```

## Running Your First Feature Test

### Option 1: Run All Feature Files

Simply run all feature files at once:

```bash
python scripts/run_features.py
```

This will execute all `.feature` files in the `features/` directory.

### Option 2: Run a Specific Feature File

Run a single feature file:

```bash
python scripts/run_features.py features/simple_examples.feature
```

Or use behave directly:

```bash
behave features/simple_examples.feature
```

## Understanding the Output

When you run feature files, you'll see output like this:

```
Feature: Voice Agent Basic Conversation
  Scenario: Simple greeting interaction
    Given a test case with id "simple_greeting"            # ✓ passed
    And the persona is "Friendly User"                     # ✓ passed
    And turn 1 where user says "Hello"                     # ✓ passed
    And the agent should respond with keywords "hello, hi" # ✓ passed
    When the test is executed                              # ✓ passed
    Then the test should pass                              # ✓ passed
    And 1 turns should be executed                         # ✓ passed

1 feature passed, 0 failed, 0 skipped
1 scenario passed, 0 failed, 0 skipped
7 steps passed, 0 failed, 0 skipped
```

- ✓ Green checkmarks indicate passing steps
- ✗ Red X marks indicate failing steps
- Each scenario is a complete test case

## Writing Your First Feature File

Create a new file `features/my_test.feature`:

```gherkin
Feature: My Voice Agent Test
  Testing my voice agent scenario

  Scenario: Customer greeting
    Given a test case with id "my_greeting_test"
    And the persona is "Polite Customer"
    And turn 1 where user says "Good morning"
    And the agent should respond with keywords "morning, hello"
    When the test is executed
    Then the test should pass
    And 1 turns should be executed
```

Then run it:

```bash
python scripts/run_features.py features/my_test.feature
```

## Loading Feature Files into Database

You can also load feature files into the database to run them via the API:

```bash
python scripts/load_features.py
```

This converts all feature files to test cases in the database. You can then run them via:

```bash
curl -X POST http://localhost:8000/test/run \
  -H "Content-Type: application/json" \
  -d '{"test_id":"my_greeting_test","provider":"twilio","mode":"simulation"}'
```

## Next Steps

- Read the complete guide: [docs/FEATURE_FILES_GUIDE.md](FEATURE_FILES_GUIDE.md)
- Look at examples in the `features/` directory
- Learn about all available steps and assertions

## Tips

- Start with simple 1-2 turn scenarios
- Use descriptive test IDs
- Choose realistic personas
- Pick keywords that uniquely identify correct responses
- Run tests frequently as you develop
