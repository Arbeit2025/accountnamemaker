import importlib.util
import os
import unittest

APP_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py"
)


def load_app():
    spec = importlib.util.spec_from_file_location("accountnamemaker_app", APP_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GenerateNamesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_app()

    def test_count_and_unique(self):
        names = self.mod.generate_names(count=10, seed=1)
        self.assertEqual(len(names), 10)
        self.assertEqual(len(names), len(set(names)))

    def test_seed_reproducible(self):
        a = self.mod.generate_names(theme="cute", count=10, seed=42)
        b = self.mod.generate_names(theme="cute", count=10, seed=42)
        self.assertEqual(a, b)

    def test_keyword_included(self):
        names = self.mod.generate_names(keyword="cocoa", count=20, seed=3)
        self.assertTrue(all("cocoa" in n for n in names))

    def test_keyword_sanitized(self):
        self.assertEqual(self.mod.sanitize_keyword(" CoCoa!! "), "cocoa")
        names = self.mod.generate_names(keyword="CoCoa!!", count=5, seed=5)
        self.assertTrue(all("cocoa" in n for n in names))

    def test_no_numbers(self):
        names = self.mod.generate_names(count=30, use_numbers=False, seed=7)
        self.assertTrue(all(not any(c.isdigit() for c in n) for n in names))

    def test_separator_none(self):
        names = self.mod.generate_names(count=30, separator="none",
                                        use_numbers=False, seed=9)
        self.assertTrue(all("_" not in n and "." not in n for n in names))

    def test_separator_dot_only(self):
        names = self.mod.generate_names(count=30, separator="dot", seed=11)
        self.assertTrue(all("_" not in n for n in names))

    def test_max_length(self):
        names = self.mod.generate_names(count=20, max_length=10, seed=13)
        self.assertTrue(all(len(n) <= 10 for n in names))

    def test_invalid_theme(self):
        with self.assertRaises(ValueError):
            self.mod.generate_names(theme="nope")

    def test_invalid_count(self):
        with self.assertRaises(ValueError):
            self.mod.generate_names(count=0)
        with self.assertRaises(ValueError):
            self.mod.generate_names(count=51)


class WebTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_app()
        cls.client = cls.mod.app.test_client()

    def test_index_ok(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        body = res.get_data(as_text=True)
        self.assertIn("Account Name Maker", body)
        self.assertIn("候補を出す", body)

    def test_index_post(self):
        res = self.client.post("/", data={
            "theme": "cute", "keyword": "cocoa", "count": "5",
            "separator": "auto", "use_numbers": "1",
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn("cocoa", res.get_data(as_text=True))

    def test_api_ok(self):
        res = self.client.get("/api/generate?theme=space&count=5&seed=1")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["count"], 5)
        self.assertEqual(len(data["names"]), 5)

    def test_api_invalid_theme_400(self):
        res = self.client.get("/api/generate?theme=nope")
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.get_json())

    def test_api_invalid_count_400(self):
        res = self.client.get("/api/generate?count=abc")
        self.assertEqual(res.status_code, 400)

    def test_healthz(self):
        res = self.client.get("/healthz")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
