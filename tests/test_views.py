import io
import tarfile
import unittest
from unittest.mock import Mock

from pyramid import testing

from augeias.views import AugeiasView, open_archive, get_archive_members


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.registry = Mock()
        self.request.registry.object_store = Mock()
        self.view = AugeiasView(self.request)

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        info = self.view.my_view()
        self.assertEqual(info["project"], "augeias")

    def test_get_container_data(self):
        collection = Mock()
        collection.object_store.get_container_data.return_value = Mock(
            read=Mock(return_value=b"zip-file")
        )
        self.request.registry.collections = {"collection": collection}
        self.request.matchdict = {
            "container_key": "container",
            "collection_key": "collection",
        }
        response = self.view.get_container_data()
        self.assertEqual(b"zip-file", response.body)

    def test_get_container_data_translations(self):
        collection = Mock()
        collection.object_store.get_container_data.return_value = Mock(
            read=Mock(return_value=b"zip-file")
        )
        self.request.GET = {
            "001": "name1.pdf",
            "002": "name2.pdf",
        }
        self.request.registry.collections = {"collection": collection}
        self.request.matchdict = {
            "container_key": "container",
            "collection_key": "collection",
        }
        response = self.view.get_container_data()
        self.assertEqual(b"zip-file", response.body)
        args, kwargs = collection.object_store.get_container_data.call_args_list[0]
        self.assertEqual(args, ("container",))
        self.assertEqual(
            kwargs,
            {
                "translations": {
                    "001": "name1.pdf",
                    "002": "name2.pdf",
                }
            },
        )


class TestArchiveHelpers(unittest.TestCase):
    def test_open_archive_tar(self):
        """Test opening a tar archive"""
        # Create a tar archive in memory
        tar_buffer = io.BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
            # Add a test file to the tar
            content = b"test content"
            tarinfo = tarfile.TarInfo(name="test.txt")
            tarinfo.size = len(content)
            tar.addfile(tarinfo, io.BytesIO(content))
        tar_buffer.seek(0)

        # Test opening the tar archive
        archive = open_archive(tar_buffer)
        self.assertIsInstance(archive, tarfile.TarFile)
        archive.close()

    def test_get_archive_members_tar(self):
        """Test extracting members from a tar archive"""
        # Create a tar archive in memory
        tar_buffer = io.BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
            # Add test files to the tar
            for name, content in [
                ("file1.txt", b"content1"),
                ("file2.txt", b"content2"),
            ]:
                tarinfo = tarfile.TarInfo(name=name)
                tarinfo.size = len(content)
                tar.addfile(tarinfo, io.BytesIO(content))
        tar_buffer.seek(0)

        # Test extracting members
        members = list(get_archive_members(tar_buffer))
        self.assertEqual(len(members), 2)
        self.assertEqual(members[0][0], "file1.txt")
        self.assertEqual(members[0][1], b"content1")
        self.assertEqual(members[1][0], "file2.txt")
        self.assertEqual(members[1][1], b"content2")
