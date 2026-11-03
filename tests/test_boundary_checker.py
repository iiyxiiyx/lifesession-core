import sys
import importlib.util
import py_compile
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lifesession.safety.boundary_checker import scan_directory


class BoundaryCheckerTests(unittest.TestCase):
    def test_own_compiled_cache_is_excluded_but_other_cache_data_is_scanned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "boundary_checker.py"
            shutil.copyfile(ROOT / "src/lifesession/safety/boundary_checker.py", source)
            cache = root / "__pycache__" / f"boundary_checker.{sys.implementation.cache_tag}.pyc"
            py_compile.compile(str(source), cfile=str(cache), doraise=True)
            self.assertTrue(cache.is_file())
            spec = importlib.util.spec_from_file_location("checker_copy", source)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.assertEqual(module.scan_directory(root), [])

            # Fake markers in an unrelated compiled module must still be found.
            other = root / "other.py"
            marker = "://".join(["ssh", "demo.invalid"])
            other.write_text("value = " + repr(marker), encoding="utf-8")
            other_cache = cache.parent / f"other.{sys.implementation.cache_tag}.pyc"
            py_compile.compile(str(other), cfile=str(other_cache), doraise=True)
            other.unlink()
            note = cache.parent / "note.txt"
            note.write_text("token" + " = " + repr("fake-demo-value"), encoding="utf-8")
            issues = module.scan_directory(root)
            self.assertTrue(any(Path(i["file"]) == other_cache and i["label"] == "SSH URL"
                                for i in issues))
            self.assertTrue(any(Path(i["file"]) == note and i["label"] == "token assignment"
                                for i in issues))

    def test_clean_examples_return_no_issues(self):
        issues = scan_directory(ROOT / "examples")

        self.assertEqual(issues, [])

    def test_internal_deploy_path_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "leak.txt"
            private_path = "/".join(["", "home", "deploy", "something"])
            path.write_text(f"Do not publish {private_path}", encoding="utf-8")

            issues = scan_directory(tmp)

        self.assertGreaterEqual(len(issues), 1)
        self.assertEqual(issues[0]["label"], "internal deploy path")

    def test_fake_ip_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ip.txt"
            fake_ip = ".".join(["192", "168", "1", "1"])
            path.write_text(f"Example private IP {fake_ip}", encoding="utf-8")

            issues = scan_directory(tmp)

        self.assertGreaterEqual(len(issues), 1)
        self.assertEqual(issues[0]["label"], "IP address")

    def test_boundary_checker_does_not_flag_its_own_source(self):
        source_dir = ROOT / "src" / "lifesession" / "safety"

        issues = scan_directory(source_dir)

        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
