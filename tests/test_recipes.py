import unittest
import tempfile

from screenie.recipes import (
        Model,
        Recipe,
        read_recipe
)


class TestReadRecipe(unittest.TestCase):

    def test_read_recipe_basic(self):
        # Create a temporary TOML file
        toml_content = """
[model]
model = "test-model"
temperature = 0.7

[criteria]
text = "Test criteria"

[prompt]
text = "Test prompt"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml') as f:
            f.write(toml_content)
            f.flush()
            temp_file = f.name
    
            recipe = read_recipe(temp_file)
    
            self.assertEqual(recipe.model.model, "test-model")
            self.assertEqual(recipe.model.temperature, 0.7)
            self.assertEqual(recipe.prompt, "Test prompt")
            self.assertEqual(recipe.criteria, "Test criteria")


    def test_read_recipe_with_missing_optional_fields(self):
        toml_content = """
[model]
model = "minimal-model"

[criteria]
text = ""

[prompt]
text = ""
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml') as f:
            f.write(toml_content)
            f.flush()
            temp_file = f.name

            recipe = read_recipe(temp_file)
            self.assertEqual(recipe.model.model, "minimal-model")
            self.assertIsNone(recipe.model.temperature)  # Should be None since not provided


    def test_read_recipe_missing_field(self):
        toml_content = """
[model]
model = "minimal-model"

[prompt]
text = ""
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml') as f:
            f.write(toml_content)
            f.flush() 
            temp_file = f.name

            with self.assertRaises(KeyError) as context:
                read_recipe(temp_file)


if __name__ == '__main__':
    unittest.main()
