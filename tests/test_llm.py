# There are some weird warning from LiteLLM. See: https://github.com/BerriAI/litellm/issues/11759
# Try to silence them but fail
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='pydantic')

import json
import unittest

from litellm import completion

from screenie.llm import (
        extract_json,
        parse_response
)


class TestExtractJSON(unittest.TestCase):

    def test_extract_json(self):
        test_str = """
        Bla bla bla 
        {
            "foo": "bar"
        }
        """
        expected_output = '{"foo": "bar"}'

        self.assertEqual(extract_json(test_str), expected_output)


    def test_no_json_error(self):
        """Test that ValueError is raised when no JSON is found"""
        test_str = """bla bla bla"""
        with self.assertRaises(ValueError):
            extract_json(test_str)


    def test_invalid_json(self):
        """Test that JSONDecodeError is raised when bad JSON is found"""
        test_str = """
        Bla Bla bla
        {
           foo: bar
        }
        """
        with self.assertRaises(json.JSONDecodeError):
            extract_json(test_str)


    def test_only_braces(self):
        """Test with only braces but no content"""
        test_str = "{}"
        result = extract_json(test_str)
        self.assertEqual(result, "{}")


class TestParseResponse(unittest.TestCase):
                      
    def test_parse_response(self):
        # Generate a mock response object
        mock_response = completion(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Test input"}],
            mock_response='bla bla bla {"verdict": 0, "reason": "believe me bro"}'
        )
        expected = {'verdict': 0, 'reason': 'believe me bro'}

        self.assertEqual(parse_response(mock_response), expected)


    def test_parse_verdict_as_str(self):
        mock_response = completion(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Test input"}],
            mock_response='bla bla bla {"verdict": "1", "reason": "believe me bro"}'
        )
        expected = {'verdict': 1, 'reason': 'believe me bro'}

        self.assertEqual(parse_response(mock_response), expected)


if __name__ == "__main__":
    unittest.main()
