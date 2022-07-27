from unittest import TestCase

from audoma.plumbing import (
    create_choices_enum_description,
    get_lib_doc_excludes_audoma,
)


class PlumbingTestCase(TestCase):
    def setUp(self):
        super().setUp()

    def test_create_choices_enum_description_dict_choices(self):
        description = create_choices_enum_description(
            {1: "One", 2: "Two", 3: "Three"}, "example_field"
        )
        self.assertEqual(
            description,
            "Filter by example_field \n * `1` - One\n * `2` - Two\n * `3` - Three\n",
        )

    def test_create_choices_enum_description_non_dict_choices(self):
        description = create_choices_enum_description(
            [(1, "One"), (2, "Two"), (3, "Three")], "example_field"
        )
        self.assertEqual(
            description,
            "Filter by example_field \n * `1` - One\n * `2` - Two\n * `3` - Three\n",
        )

    # TODO - find out how we should test this method
    def test_get_lib_doc_excludes_audoma(self):
        ...
