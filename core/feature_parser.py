"""Parser to convert Gherkin feature files to TestCase objects."""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from models.test_cases import TestCase, TurnExpectation


class FeatureFileParser:
    """Parse Gherkin feature files and convert to TestCase objects."""
    
    # Regex patterns for parsing Gherkin steps
    PATTERN_TEST_ID = r'Given a test case with id "([^"]+)"'
    PATTERN_PERSONA = r'(?:Given|And) the persona is "([^"]+)"'
    PATTERN_TURN_INPUT = r'(?:Given|And) turn (\d+) where user says "([^"]+)"'
    PATTERN_KEYWORDS = r'(?:Given|And) the agent should respond with keywords "([^"]+)"'
    PATTERN_EXACT_MATCH = r'(?:Given|And) exact match is required'
    
    def __init__(self, feature_file: str | Path) -> None:
        """Initialize parser with a feature file path."""
        self.feature_file = Path(feature_file)
        if not self.feature_file.exists():
            raise FileNotFoundError(f"Feature file not found: {feature_file}")
    
    def parse(self) -> List[TestCase]:
        """Parse the feature file and return a list of TestCase objects."""
        with open(self.feature_file, 'r') as f:
            content = f.read()
        
        test_cases = []
        scenarios = self._extract_scenarios(content)
        
        for scenario in scenarios:
            test_case = self._parse_scenario(scenario)
            if test_case:
                test_cases.append(test_case)
        
        return test_cases
    
    def _extract_scenarios(self, content: str) -> List[str]:
        """Extract individual scenarios from the feature file."""
        # Split on "Scenario:" but keep the marker
        scenarios = re.split(r'(?=Scenario:)', content)
        # Filter out the feature header and empty strings
        return [s.strip() for s in scenarios if 'Scenario:' in s]
    
    def _parse_scenario(self, scenario_text: str) -> Optional[TestCase]:
        """Parse a single scenario into a TestCase object."""
        lines = scenario_text.split('\n')
        
        # Extract scenario name
        scenario_name = None
        for line in lines:
            if line.strip().startswith('Scenario:'):
                scenario_name = line.split('Scenario:')[1].strip()
                break
        
        if not scenario_name:
            return None
        
        # Parse scenario steps
        test_id = None
        persona = "Default Persona"
        turns: List[TurnExpectation] = []
        current_turn: dict = {}
        
        for line in lines:
            line = line.strip()
            
            # Parse test ID
            match = re.match(self.PATTERN_TEST_ID, line)
            if match:
                test_id = match.group(1)
                continue
            
            # Parse persona
            match = re.match(self.PATTERN_PERSONA, line)
            if match:
                persona = match.group(1)
                continue
            
            # Parse turn user input
            match = re.match(self.PATTERN_TURN_INPUT, line)
            if match:
                if current_turn:
                    # Save previous turn
                    turns.append(TurnExpectation(**current_turn))
                current_turn = {
                    'step_order': int(match.group(1)),
                    'user_input': match.group(2),
                    'exact_match_required': False,
                }
                continue
            
            # Parse agent response keywords
            match = re.match(self.PATTERN_KEYWORDS, line)
            if match:
                keywords = [k.strip() for k in match.group(1).split(',')]
                current_turn['expected_agent_response_keywords'] = keywords
                # Complete the turn
                if current_turn:
                    turns.append(TurnExpectation(**current_turn))
                    current_turn = {}
                continue
            
            # Parse exact match requirement
            if re.match(self.PATTERN_EXACT_MATCH, line):
                if current_turn:
                    current_turn['exact_match_required'] = True
                continue
        
        # Create test case
        if not test_id:
            # Generate test ID from scenario name with warning
            test_id = re.sub(r'[^a-z0-9]+', '_', scenario_name.lower())
            import warnings
            warnings.warn(
                f"No test_id specified for scenario '{scenario_name}'. "
                f"Auto-generated ID: '{test_id}'. "
                f"Please specify a test_id to avoid potential conflicts.",
                UserWarning
            )
        
        if not turns:
            return None
        
        return TestCase(
            test_id=test_id,
            persona=persona,
            turns=turns
        )


def load_feature_file(feature_file: str | Path) -> List[TestCase]:
    """Helper function to load test cases from a feature file."""
    parser = FeatureFileParser(feature_file)
    return parser.parse()


def load_all_features(features_dir: str | Path = "features") -> List[TestCase]:
    """Load all test cases from all feature files in a directory."""
    features_path = Path(features_dir)
    if not features_path.exists():
        return []
    
    all_test_cases = []
    for feature_file in features_path.glob("*.feature"):
        test_cases = load_feature_file(feature_file)
        all_test_cases.extend(test_cases)
    
    return all_test_cases
