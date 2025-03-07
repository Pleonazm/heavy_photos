import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from hp_storage import DataStorageIndexJSON  # Adjust module import accordingly


@pytest.fixture
def temp_file(tmp_path):
    file = tmp_path / "test_data.json"
    file.write_text("[]", encoding="utf-8")  # Initialize as empty JSON list
    return file

@pytest.fixture
def data_storage(temp_file):
    return DataStorageIndexJSON(uri=temp_file)

def test_make(data_storage):
    assert data_storage.make() is True
    assert data_storage.uri.exists()

def test_add_and_get(data_storage):
    data = {"id": "123", "name": "Test Item"}
    data_storage.add(data)
    assert data_storage.get("123") == data

def test_get_all(data_storage):
    data_storage.uri.write_text(json.dumps([{"id": "1"}, {"id": "2"}]))
    assert len(data_storage.get_all()) == 2

def test_find(data_storage):
    data_storage.full_index_data = [{"id": "1", "name": "Alpha"}, {"id": "2", "name": "Beta"}]
    result = data_storage.find({"name": "Beta"})
    assert result == [{"id": "2", "name": "Beta"}]

def test_update(data_storage):
    data_storage.full_index_data = [{"id": "1", "name": "Old"}]
    updated = data_storage.update("1", {"name": "New"})
    assert updated["name"] == "New"

def test_delete(data_storage):
    data_storage.full_index_data = [{"id": "1"}]
    data_storage.delete("1")
    assert data_storage.full_index_data == []

def test_remake(data_storage):
    data_storage.full_index_data = [{"id": "1", "name": "Save Test"}]
    data_storage.remake(forced=True)
    assert json.loads(data_storage.uri.read_text())[0]["name"] == "Save Test"

def test_unmake(data_storage):
    data_storage.remake(forced=True)
    assert data_storage.unmake() is True
    assert not data_storage.uri.exists()

def test_get_nonexistent(data_storage):
    assert data_storage.get("999") is None

def test_find_nonexistent(data_storage):
    result = data_storage.find({"name": "Nonexistent"})
    assert result == []

def test_update_nonexistent(data_storage):
    updated = data_storage.update("999", {"name": "Doesn't Exist"})
    assert updated == {}

def test_delete_nonexistent(data_storage):
    data_storage.delete("999")  # Should not raise an error
    assert data_storage.full_index_data == []

# Mock-based tests (alternative to actual file operations)
@pytest.fixture
def mock_storage():
    with patch("pathlib.Path.write_text") as mock_write, \
         patch("pathlib.Path.read_text", return_value=json.dumps([])) as mock_read, \
         patch("pathlib.Path.unlink") as mock_unlink, \
         patch("pathlib.Path.exists", return_value=True) as mock_exists:
        storage = DataStorageIndexJSON(uri="mocked_path.json")
        yield storage, mock_write, mock_read, mock_unlink, mock_exists

def test_mock_remake(mock_storage):
    storage, mock_write, _, _, _ = mock_storage
    storage.full_index_data = [{"id": "1", "name": "Mock Test"}]
    storage.remake(forced=True)
    mock_write.assert_called_once()

def test_mock_unmake(mock_storage):
    storage, _, _, mock_unlink, _ = mock_storage
    assert storage.unmake() is True
    mock_unlink.assert_called_once()

def test_mock_make(mock_storage):
    storage, _, _, _, mock_exists = mock_storage
    assert storage.make() is True
    mock_exists.assert_called()

def test_mock_get_all(mock_storage):
    storage, _, mock_read, _, _ = mock_storage
    assert storage.get_all() == []  # Mocked empty JSON list
    mock_read.assert_called_once()
