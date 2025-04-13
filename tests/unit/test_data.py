"""
Unit tests for the data module.
"""

import pytest
from pathlib import Path
import os
import json

from word_atlas.data import (
    get_data_dir,
    get_word_index,
    get_word_frequencies,
)

# Import the data module itself to access __file__
from word_atlas import data as word_atlas_data

# Helper function to create minimal valid data dir structure
def create_minimal_data_structure(base_path: Path):
    base_path.mkdir(parents=True, exist_ok=True)
    (base_path / "word_index.json").write_text('{"test": 0}')
    freq_dir = base_path / "frequencies"
    freq_dir.mkdir()
    (freq_dir / "word_frequencies.json").write_text('{"test": 1.0}')
    sources_dir = base_path / "sources"
    sources_dir.mkdir()
    (sources_dir / "dummy.json").touch() # Need at least one file in sources


def test_get_data_dir(mock_data_dir):
    """Test finding the data directory with explicit path."""
    # Test with explicit path
    data_dir = get_data_dir(mock_data_dir)
    assert isinstance(data_dir, Path)
    assert data_dir.exists()

    # Test required files exist (index, frequencies, sources dir)
    assert (data_dir / "word_index.json").exists()
    assert (data_dir / "frequencies" / "word_frequencies.json").exists()
    assert (data_dir / "sources").is_dir()

    # Test with invalid explicit path
    with pytest.raises(FileNotFoundError):
        get_data_dir("/nonexistent/path")


def test_get_data_dir_search_logic(tmp_path, monkeypatch):
    """Test the search logic of get_data_dir for default locations."""
    original_cwd = Path.cwd()
    real_package_data_path = Path(word_atlas_data.__file__).parent.parent / "data"
    original_home = Path.home()

    # --- Define temp paths ---
    cwd_data_path = tmp_path / "data"
    pkg_subdir = tmp_path / "pkg_subdir"
    pkg_data_path = pkg_subdir / "data"
    home_subdir = tmp_path / "home"
    home_data_path = home_subdir / "english_word_atlas" / "data"

    # --- Helper to mock existence of real paths --- 
    def setup_mocks(mp, ignore_pkg=False, ignore_home=False):
        original_path_exists = Path.exists
        original_is_dir = Path.is_dir
        
        def mocked_exists(path_obj):
            print(f"[DEBUG exists] Checking: {path_obj}") # DEBUG
            # --- Handle Ignored Paths ---
            if ignore_pkg and path_obj == real_package_data_path:
                print(f"[DEBUG exists] -> Ignored (pkg): False") # DEBUG
                return False
            if ignore_home and path_obj == original_home / "english_word_atlas" / "data":
                print(f"[DEBUG exists] -> Ignored (home): False") # DEBUG
                return False
            if str(path_obj).startswith('/usr/local/share/english_word_atlas'):
                print(f"[DEBUG exists] -> Ignored (system): False") # DEBUG
                return False
                
            # --- Handle Real Paths Contents (when *not* ignored) ---
            # If checking contents of real package path (and not ignoring pkg), deny existence
            if not ignore_pkg and path_obj != real_package_data_path and str(path_obj).startswith(str(real_package_data_path)):
                 print(f"[DEBUG exists] -> Denied (real pkg content): False") # DEBUG
                 return False
             # If checking contents of real home path (and not ignoring home), deny existence
            real_home_data_path = original_home / "english_word_atlas" / "data"
            if not ignore_home and path_obj != real_home_data_path and str(path_obj).startswith(str(real_home_data_path)):
                 print(f"[DEBUG exists] -> Denied (real home content): False") # DEBUG
                 return False

            # --- Otherwise, check actual existence (for temp paths etc.) ---
            result = original_path_exists(path_obj)
            print(f"[DEBUG exists] -> Original check: {result}") # DEBUG
            return result
        
        mp.setattr(Path, "exists", mocked_exists)
        
        # We also need to mock is_dir check for sources/
        def mocked_is_dir(path_obj):
            print(f"[DEBUG is_dir] Checking: {path_obj}") # DEBUG
             # --- Handle Ignored Paths ---
            if ignore_pkg and path_obj == real_package_data_path / "sources":
                print(f"[DEBUG is_dir] -> Ignored (pkg sources): False") # DEBUG
                return False
            if ignore_home and path_obj == original_home / "english_word_atlas" / "data" / "sources":
                print(f"[DEBUG is_dir] -> Ignored (home sources): False") # DEBUG
                return False
            if str(path_obj).startswith('/usr/local/share/english_word_atlas/data/sources'):
                print(f"[DEBUG is_dir] -> Ignored (system sources): False") # DEBUG
                return False
                
            # --- Handle Real Paths Contents (when *not* ignored) ---
            # Deny is_dir check for real sources dir if not ignoring pkg/home respectively
            if not ignore_pkg and path_obj == real_package_data_path / "sources":
                 print(f"[DEBUG is_dir] -> Denied (real pkg sources): False") # DEBUG
                 return False
            if not ignore_home and path_obj == original_home / "english_word_atlas" / "data" / "sources":
                 print(f"[DEBUG is_dir] -> Denied (real home sources): False") # DEBUG
                 return False
                 
            # --- Otherwise, check actual is_dir (for temp paths etc.) ---
            # Specifically allow check for temp sources dirs
            if path_obj in [cwd_data_path / "sources", pkg_data_path / "sources", home_data_path / "sources"]:
                 result = original_is_dir(path_obj)
                 print(f"[DEBUG is_dir] -> Temp sources check: {result}") # DEBUG
                 return result
                 
            # Fallback for other paths (should ideally not be needed often)
            result = original_is_dir(path_obj)
            print(f"[DEBUG is_dir] -> Original check: {result}") # DEBUG
            return result
        mp.setattr(Path, "is_dir", mocked_is_dir)

    try:
        # --- Test 1: Current Directory --- 
        with monkeypatch.context() as mp1:
            setup_mocks(mp1, ignore_pkg=True, ignore_home=True) # Ignore real pkg & home
            mp1.setattr(Path, "cwd", lambda: tmp_path)
            create_minimal_data_structure(cwd_data_path)
            assert get_data_dir() == cwd_data_path
            # Clean up test 1 files
            os.remove(cwd_data_path / "word_index.json") 
            os.remove(cwd_data_path / "frequencies/word_frequencies.json")
            os.remove(cwd_data_path / "sources/dummy.json")
            os.rmdir(cwd_data_path / "frequencies")
            os.rmdir(cwd_data_path / "sources")
            os.rmdir(cwd_data_path)
            
        # --- Test 2: Package Directory --- 
        # Mock __file__ so Path(__file__).parent.parent / "data" points to temp pkg path
        with monkeypatch.context() as mp2:
            setup_mocks(mp2, ignore_pkg=False, ignore_home=True) # Check package path, ignore real home
            # Create a dummy file within the temp package structure to set __file__
            dummy_module_path = pkg_subdir / "word_atlas" / "data.py"
            dummy_module_path.parent.mkdir(parents=True)
            dummy_module_path.touch()
            mp2.setattr(word_atlas_data, "__file__", str(dummy_module_path)) # Critical step
            
            create_minimal_data_structure(pkg_data_path)
            assert get_data_dir() == pkg_data_path 
            # Clean up test 2 files
            os.remove(pkg_data_path / "word_index.json")
            os.remove(pkg_data_path / "frequencies/word_frequencies.json")
            os.remove(pkg_data_path / "sources/dummy.json")
            os.rmdir(pkg_data_path / "frequencies")
            os.rmdir(pkg_data_path / "sources")
            os.rmdir(pkg_data_path)
            os.remove(dummy_module_path)
            os.rmdir(dummy_module_path.parent)
            os.rmdir(pkg_subdir)

        # --- Test 3: Home Directory --- 
        with monkeypatch.context() as mp3:
            setup_mocks(mp3, ignore_pkg=True, ignore_home=False) # Ignore real pkg, check home
            mp3.setattr(Path, "home", lambda: home_subdir)
            create_minimal_data_structure(home_data_path)
            assert get_data_dir() == home_data_path
            # Clean up test 3 files
            os.remove(home_data_path / "word_index.json")
            os.remove(home_data_path / "frequencies/word_frequencies.json")
            os.remove(home_data_path / "sources/dummy.json")
            os.rmdir(home_data_path / "frequencies")
            os.rmdir(home_data_path / "sources")
            os.rmdir(home_data_path)
            os.rmdir(home_data_path.parent)
            os.rmdir(home_subdir)

        # --- Test 4: FileNotFoundError --- 
        with monkeypatch.context() as mp4:
            setup_mocks(mp4, ignore_pkg=True, ignore_home=True) # Ignore all real paths
            with pytest.raises(FileNotFoundError):
                get_data_dir()
                
    finally:
        os.chdir(original_cwd) # Restore original CWD

def test_get_word_index(mock_data_dir):
    """Test getting the word index mapping."""
    word_index = get_word_index(mock_data_dir)

    # Check structure
    assert isinstance(word_index, dict)
    assert len(word_index) > 0

    # Check specific words from our mock data
    assert "apple" in word_index
    assert "banana" in word_index

    # Check index values
    assert isinstance(word_index["apple"], int)
    assert isinstance(word_index["banana"], int)

    # Check indices are sequential starting from 0
    indices = sorted(word_index.values())
    assert indices == list(range(len(indices)))


def test_get_word_frequencies(mock_data_dir):
    """Test getting word frequencies."""
    word_frequencies = get_word_frequencies(mock_data_dir)

    # Check structure
    assert isinstance(word_frequencies, dict)
    assert len(word_frequencies) > 0

    # Check specific words from our mock data
    assert "apple" in word_frequencies
    assert "banana" in word_frequencies
    assert "orange" in word_frequencies

    # Check word frequencies
    assert isinstance(word_frequencies["apple"], float)
    assert isinstance(word_frequencies["banana"], float)
    assert isinstance(word_frequencies["orange"], float)

# Add tests for error handling in get_word_frequencies
def test_get_word_frequencies_errors(tmp_path, monkeypatch):
    """Test error handling for get_word_frequencies."""
    # Mock get_data_dir to return our temp path
    monkeypatch.setattr('word_atlas.data.get_data_dir', lambda x=None: tmp_path)
    freq_dir = tmp_path / "frequencies"
    freq_file = freq_dir / "word_frequencies.json"

    # 1. Test FileNotFoundError
    with pytest.raises(FileNotFoundError):
        get_word_frequencies()

    # Create directory but not file
    freq_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        get_word_frequencies()

    # 2. Test JSONDecodeError (ValueError)
    freq_file.write_text("invalid json")
    with pytest.raises(ValueError):
        get_word_frequencies()
    freq_file.unlink() # Clean up

    # 3. Test PermissionError (RuntimeError)
    # Create valid json first
    freq_file.write_text('{"a": 1.0}')
    # Make file unreadable (adjust permissions as needed for OS)
    os.chmod(freq_file, 0o000)
    with pytest.raises(RuntimeError): # Catches the generic Exception
        get_word_frequencies()
    # Restore permissions to allow cleanup
    os.chmod(freq_file, 0o644)
