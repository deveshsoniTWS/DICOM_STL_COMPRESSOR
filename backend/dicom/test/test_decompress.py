"""
dicom/test/test_decompress.py

Full validation suite:
  1. Lossless round trip — bit-perfect pixel check
  2. Lossy round trip — visual quality metrics (PSNR, max diff, mean diff)
  3. Metadata preservation — key tags survive round trip
  4. File integrity — reconstructed .dcm is readable by pydicom
  5. Shape/dtype preservation — array dimensions and type match
"""

import io
import os
import sys

import numpy as np
import pydicom

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dicom.compress import compress
from dicom.decompress import decompress

FILES_DIR = os.path.join(os.path.dirname(__file__), "files")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─── HELPERS ──────────────────────────────────────────────────────────────────


def get_dicom_files() -> list[str]:
    return [
        os.path.join(FILES_DIR, f) for f in os.listdir(FILES_DIR) if f.endswith(".dcm")
    ]


def read_pixels(dcm_bytes: bytes) -> np.ndarray:
    return pydicom.dcmread(io.BytesIO(dcm_bytes)).pixel_array


def psnr(original: np.ndarray, reconstructed: np.ndarray) -> float:
    """Peak Signal-to-Noise Ratio — higher is better. >40dB is excellent."""
    mse = np.mean((original.astype(np.float64) - reconstructed.astype(np.float64)) ** 2)
    if mse == 0:
        return float("inf")
    max_val = 255.0 if original.dtype == np.uint8 else 65535.0
    return round(20 * np.log10(max_val / np.sqrt(mse)), 2)


def save_output(name: str, data: bytes):
    path = os.path.join(OUTPUT_DIR, name)
    with open(path, "wb") as f:
        f.write(data)
    return path


# ─── TESTS ────────────────────────────────────────────────────────────────────


def test_lossless_bit_perfect(path: str) -> bool:
    """
    Lossless round trip must produce bit-perfect pixels.
    Any difference = pipeline bug.
    """
    name = os.path.basename(path)
    print(f"\n{'─' * 50}")
    print(f"[LOSSLESS BIT-PERFECT] {name}")

    original_ds = pydicom.dcmread(path)
    original_pixels = original_ds.pixel_array

    compressed, stats = compress(path, mode="lossless")
    dcm_bytes, _ = decompress(compressed)

    # Save reconstructed file for manual inspection
    out_path = save_output(f"{name}_lossless_reconstructed.dcm", dcm_bytes)

    reconstructed_pixels = read_pixels(dcm_bytes)

    # ── Checks ────────────────────────────────────────────────────────────────
    checks = {}

    checks["shape_match"] = original_pixels.shape == reconstructed_pixels.shape
    checks["dtype_match"] = original_pixels.dtype == reconstructed_pixels.dtype
    checks["bit_perfect"] = bool(np.array_equal(original_pixels, reconstructed_pixels))

    max_diff = int(
        np.max(np.abs(original_pixels.astype(int) - reconstructed_pixels.astype(int)))
    )
    mean_diff = float(
        np.mean(np.abs(original_pixels.astype(int) - reconstructed_pixels.astype(int)))
    )

    # ── Print ──────────────────────────────────────────────────────────────────
    print(
        f"  Original shape:       {original_pixels.shape}  dtype: {original_pixels.dtype}"
    )
    print(
        f"  Reconstructed shape:  {reconstructed_pixels.shape}  dtype: {reconstructed_pixels.dtype}"
    )
    print(f"  Compression ratio:    {stats['compression_ratio_pct']}%")
    print(f"  Max pixel diff:       {max_diff}  (must be 0)")
    print(f"  Mean pixel diff:      {mean_diff:.6f}  (must be 0.0)")
    print(
        f"  PSNR:                 {psnr(original_pixels, reconstructed_pixels)} dB  (inf = perfect)"
    )
    print(f"  Reconstructed saved:  {out_path}")

    passed = all(checks.values())
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")

    return passed


def test_lossy_quality(path: str) -> bool:
    """
    Lossy round trip — pixels won't be identical.
    Check PSNR > 30dB and compression hits target.
    """
    name = os.path.basename(path)
    print(f"\n{'─' * 50}")
    print(f"[LOSSY QUALITY] {name}")

    original_ds = pydicom.dcmread(path)
    original_pixels = original_ds.pixel_array

    compressed, stats = compress(path, mode="lossy")
    dcm_bytes, _ = decompress(compressed)

    out_path = save_output(f"{name}_lossy_reconstructed.dcm", dcm_bytes)

    reconstructed_pixels = read_pixels(dcm_bytes)

    checks = {}
    checks["shape_match"] = original_pixels.shape == reconstructed_pixels.shape
    checks["dtype_match"] = original_pixels.dtype == reconstructed_pixels.dtype
    checks["psnr_above_30"] = psnr(original_pixels, reconstructed_pixels) > 30.0
    checks["ratio_above_50"] = stats["compression_ratio_pct"] > 50.0

    max_diff = int(
        np.max(np.abs(original_pixels.astype(int) - reconstructed_pixels.astype(int)))
    )
    mean_diff = float(
        np.mean(np.abs(original_pixels.astype(int) - reconstructed_pixels.astype(int)))
    )
    psnr_val = psnr(original_pixels, reconstructed_pixels)

    print(
        f"  Original shape:       {original_pixels.shape}  dtype: {original_pixels.dtype}"
    )
    print(
        f"  Reconstructed shape:  {reconstructed_pixels.shape}  dtype: {reconstructed_pixels.dtype}"
    )
    print(f"  Compression ratio:    {stats['compression_ratio_pct']}%")
    print(f"  Max pixel diff:       {max_diff}")
    print(f"  Mean pixel diff:      {mean_diff:.4f}")
    print(f"  PSNR:                 {psnr_val} dB  (>30dB = good, >40dB = excellent)")
    print(f"  Reconstructed saved:  {out_path}")

    passed = all(checks.values())
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")

    return passed


def test_metadata_preserved(path: str) -> bool:
    """
    Key DICOM tags should survive the round trip.
    """
    name = os.path.basename(path)
    print(f"\n{'─' * 50}")
    print(f"[METADATA PRESERVATION] {name}")

    original_ds = pydicom.dcmread(path)

    compressed, _ = compress(path, mode="lossless")
    dcm_bytes, _ = decompress(compressed)

    reconstructed_ds = pydicom.dcmread(io.BytesIO(dcm_bytes))

    tags_to_check = [
        "Rows",
        "Columns",
        "BitsAllocated",
        "BitsStored",
        "SamplesPerPixel",
        "PhotometricInterpretation",
        "Modality",
        "PatientID",
    ]

    checks = {}
    for tag in tags_to_check:
        orig_val = str(getattr(original_ds, tag, "MISSING"))
        recon_val = str(getattr(reconstructed_ds, tag, "MISSING"))
        match = orig_val == recon_val
        checks[tag] = match
        status = "✅" if match else "❌"
        print(f"  {status} {tag}: '{orig_val}' → '{recon_val}'")

    return all(checks.values())


def test_file_integrity(path: str) -> bool:
    """
    Reconstructed .dcm must be readable by pydicom without errors.
    """
    name = os.path.basename(path)
    print(f"\n{'─' * 50}")
    print(f"[FILE INTEGRITY] {name}")

    for mode in ("lossless", "lossy"):
        compressed, _ = compress(path, mode=mode)
        dcm_bytes, _ = decompress(compressed)

        try:
            ds = pydicom.dcmread(io.BytesIO(dcm_bytes))
            _ = ds.pixel_array  # force pixel decode
            print(f"  ✅ {mode} — readable, pixel decode OK")
        except Exception as e:
            print(f"  ❌ {mode} — {e}")
            return False

    return True


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    files = get_dicom_files()

    if not files:
        print(f"No .dcm files found in: {FILES_DIR}")
        print("Drop DICOM files into dicom/test/files/ and re-run.")
        sys.exit(1)

    print(f"Found {len(files)} DICOM file(s)\n")

    total = 0
    passed = 0

    for path in files:
        for test_fn in [
            test_lossless_bit_perfect,
            test_lossy_quality,
            test_metadata_preserved,
            test_file_integrity,
        ]:
            total += 1
            try:
                result = test_fn(path)
                if result:
                    passed += 1
            except Exception as e:
                print(f"  ❌ EXCEPTION in {test_fn.__name__}: {e}")

    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{total} passed")

    if passed < total:
        sys.exit(1)
