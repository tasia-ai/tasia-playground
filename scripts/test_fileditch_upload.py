import json
import unittest

from fileditch_upload import UploadError, upload_path, validate_result


class FileDitchUploadTests(unittest.TestCase):
    def test_upload_path_encodes_filename(self):
        self.assertEqual(upload_path("Tasia Viewer #1.zip"), "/upload.php?filename=Tasia+Viewer+%231.zip")

    def test_accepts_expected_upload_confirmation(self):
        result = validate_result(
            json.dumps(
                {
                    "success": True,
                    "url": "https://itsfileditchfiles.st/a/file.zip",
                    "filename": "file.zip",
                    "size": 4,
                }
            ).encode(),
            "file.zip",
            4,
        )
        self.assertEqual(result["url"], "https://itsfileditchfiles.st/a/file.zip")

    def test_rejects_untrusted_or_mismatched_confirmation(self):
        for url, returned_name in (
            ("http://itsfileditchfiles.st/a/file.zip", "file.zip"),
            ("https://example.com/a/file.zip", "file.zip"),
            ("https://itsfileditchfiles.st/a/file.zip", "other.zip"),
        ):
            with self.subTest(url=url, returned_name=returned_name), self.assertRaises(UploadError):
                validate_result(
                    json.dumps(
                        {"success": True, "url": url, "filename": returned_name, "size": 4}
                    ).encode(),
                    "file.zip",
                    4,
                )


if __name__ == "__main__":
    unittest.main()
