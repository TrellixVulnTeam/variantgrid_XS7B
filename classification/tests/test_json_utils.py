from unittest import TestCase
from uicore.json.validated_json import JsonMessages, ValidatedJson


class JsonUtilTests(TestCase):

    def test_validate_json(self):
        original = ValidatedJson({
            "normal": 3,
            "validated": ValidatedJson(
                [
                    1,
                    ValidatedJson(2, JsonMessages.info("This is the number 2"))
                ]
                , JsonMessages.info("This is a list of numbers"))
        })
        serialized = original.serialize()
        deserialized = ValidatedJson.deserialize(serialized)
        self.assertEqual(original, deserialized)

        self.assertEqual(original.pure_json(), {"normal": 3, "validated": [1, 2]})
