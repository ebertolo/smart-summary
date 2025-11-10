"""
Setup script to download NLTK data before running tests
"""

import os

import nltk


def setup_nltk():
    """Download required NLTK data"""
    print("=" * 60)
    print("Setting up NLTK data for tests...")
    print("=" * 60)

    # Set NLTK data path
    nltk_data_paths = [
        os.path.expanduser("~/nltk_data"),
        os.path.expanduser("~\\nltk_data"),  # Windows
    ]

    for path in nltk_data_paths:
        if path not in nltk.data.path:
            nltk.data.path.append(path)
            print(f"Added NLTK path: {path}")

    # Packages to download
    packages = [
        ("punkt", "tokenizers/punkt"),
        ("punkt_tab", "tokenizers/punkt_tab"),
        ("stopwords", "corpora/stopwords"),
    ]

    success_count = 0
    for package_name, package_path in packages:
        print(f"\nChecking {package_name}...")

        try:
            # Check if already exists
            nltk.data.find(package_path)
            print(f"  ✓ {package_name} already installed")
            success_count += 1
        except LookupError:
            # Download
            print(f"  Downloading {package_name}...")
            try:
                nltk.download(package_name, quiet=False)
                print(f"  ✓ Successfully downloaded {package_name}")
                success_count += 1
            except Exception as e:
                print(f"  ✗ Failed to download {package_name}: {e}")

                # Try alternative download method
                try:
                    download_dir = os.path.expanduser("~/nltk_data")
                    os.makedirs(download_dir, exist_ok=True)
                    nltk.download(package_name, download_dir=download_dir, quiet=False)
                    print(f"  ✓ Downloaded {package_name} to {download_dir}")
                    success_count += 1
                except Exception as e2:
                    print(f"  ✗ Alternative download also failed: {e2}")

    print("\n" + "=" * 60)
    print(f"NLTK setup complete: {success_count}/{len(packages)} packages ready")
    print("=" * 60)

    if success_count < len(packages):
        print("\nWARNING: Some packages failed to download.")
        print("Tests will use fallback methods, but results may vary.")
        print("\nYou can manually download NLTK data by running:")
        print(
            "  python -c \"import nltk; nltk.download('punkt'); nltk.download('punkt_tab')\""
        )

    return success_count == len(packages)


if __name__ == "__main__":
    success = setup_nltk()
    exit(0 if success else 1)
