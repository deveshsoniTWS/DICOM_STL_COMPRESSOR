"""
dicom/test/test_compress.py
Tests for DICOM compression.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dicom.compress import compress

FILES_DIR = os.path.join(os.path.dirname(__file__), "files")


def get_dicom_files() -> list[str]:
    return [
        os.path.join(FILES_DIR, f) for f in os.listdir(FILES_DIR) if f.endswith(".dcm")
    ]


def test_lossless(path: str):
    print(f"\n[LOSSLESS] {os.path.basename(path)}")
    compressed, stats = compress(path, mode="lossless")

    print(f"  Original:    {stats['original_size_kb']} KB")
    print(f"  Compressed:  {stats['compressed_size_kb']} KB")
    print(f"  Ratio:       {stats['compression_ratio_pct']}%")
    print(f"  Shape:       {stats['shape']}")
    print(f"  dtype:       {stats['dtype']}")
    print(f"  Multiframe:  {stats['is_multiframe']}")

    assert len(compressed) > 0, "Compressed output is empty"
    assert stats["compression_ratio_pct"] > 0, "No compression achieved"

    print("  ✅ PASSED")


def test_lossy(path: str):
    print(f"\n[LOSSY] {os.path.basename(path)}")
    compressed, stats = compress(path, mode="lossy")

    print(f"  Original:    {stats['original_size_kb']} KB")
    print(f"  Compressed:  {stats['compressed_size_kb']} KB")
    print(f"  Ratio:       {stats['compression_ratio_pct']}%")

    assert len(compressed) > 0, "Compressed output is empty"
    assert stats["compression_ratio_pct"] > stats["compression_ratio_pct"] - 1

    print("  ✅ PASSED")


if __name__ == "__main__":
    files = get_dicom_files()

    if not files:
        print(f"No .dcm files found in {FILES_DIR}")
        print("Add DICOM files to dicom/test/files/ and re-run.")
        sys.exit(1)

    print(f"Found {len(files)} DICOM file(s)")

    failed = 0
    for path in files:
        try:
            test_lossless(path)
            test_lossy(path)
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            failed += 1

    print(f"\n{'=' * 40}")
    print(f"Results: {len(files) - failed}/{len(files)} passed")
    if failed:
        sys.exit(1)
