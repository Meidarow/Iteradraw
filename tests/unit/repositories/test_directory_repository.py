from pathlib import Path

from hypothesis import given, strategies as st, settings, HealthCheck


class TestSQLite3DirectoryRepository:
    class TestCreateDirectories:
        def test_create_directories_functionality(
                self,
                sqlite_directory_repo,
                sqlite_database_in_memory
        ):
            repo = sqlite_directory_repo
            db = sqlite_database_in_memory
            query = """
            SELECT dir_name FROM directories WHERE dir_name = ?
            """
            for i in range(10):
                folder = "Test/folder_%i" % i
                repo.create_directories([Path(folder)])
                assert folder in db.execute(query, (folder,)).fetchone()

    class TestGetNormalizedPath:
        @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
        @given(path_str=st.from_regex(r"([^/]{2,10}/){1,8}([\w]{1,8})"))
        def test_get_normalized_path_functionality(
                self,
                path_str,
                sqlite_directory_repo,
                sqlite_database_in_memory
        ):
            db = sqlite_database_in_memory
            repo = sqlite_directory_repo
            query_node = """
            INSERT INTO directories (dir_name, crawl_time, mod_time) VALUES 
            (?, 0, 0) RETURNING dir_id
            """
            query_closure = ("INSERT INTO folders_closure (ancestor_id, "
                             "descendant_id, depth) VALUES (?, ?, 0)")

            dir_id = db.execute(query_node, (path_str,)).fetchone()["dir_id"]
            db.execute(query_closure, (dir_id, dir_id))

            assert repo.get_normalized_path(dir_id) == Path(path_str)

    class TestIsDuplicate:
        @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
        @given(path_str=st.from_regex(r"([^/]{2,10}/){1,8}([\w]{1,8})"))
        def test_is_duplicate_functionality(
                self,
                path_str,
                sqlite_directory_repo,
                sqlite_database_in_memory
        ):
            query_node = """
            INSERT INTO directories (dir_name, crawl_time, mod_time) VALUES 
            (?, 0, 0) RETURNING dir_id
            """
            query_closure = ("INSERT INTO folders_closure (ancestor_id, "
                             "descendant_id, depth) VALUES (?, ?, 0)")

            assert sqlite_directory_repo.is_duplicate(Path(path_str)) == 0
            dir_id = sqlite_database_in_memory.execute(
                query_node,
                (path_str,)).fetchone()["dir_id"]
            sqlite_database_in_memory.execute(query_closure, (dir_id, dir_id))
            assert sqlite_directory_repo.is_duplicate(Path(path_str)) != 0

            sqlite_database_in_memory.execute("DELETE FROM folders_closure")
            sqlite_database_in_memory.execute("DELETE FROM directories")

    class TestGetDirectories:
        ...

    class TestCreateDirectory:
        def test_create_directory_functionality(
                self,
                sqlite_directory_repo,
                sqlite_database_in_memory
        ):
            ...

    class TestUpdateDirectory:
        ...

    class TestBuildDirectoryGraph:
        ...

    class TestRegisterNode:
        ...

    class TestRegisterNodeBatch:
        @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
        @given(folders=st.lists(
            st.from_regex(r"(/[^/]{2,12}){2,12}"),
            max_size=2
        ))
        def test_register_node_batch_functionality(
                self,
                sqlite_directory_repo,
                sqlite_database_in_memory,
                folders
        ):
            repo = sqlite_directory_repo
            db = sqlite_database_in_memory
            dirs = set(folders)
            dir_ids = set(repo._register_node_batch(folders))
            query = """
            SELECT dir_name, dir_id FROM directories ORDER BY dir_id ASC
            """
            dirs_inserted = set()
            dir_ids_inserted = set()
            for row in db.execute(query).fetchall():
                dirs_inserted.add(row["dir_name"])
                dir_ids_inserted.add(row["dir_id"])

            assert dirs_inserted == dirs
            assert dir_ids_inserted == dir_ids
            db.execute("DELETE FROM directories")

    class TestRegisterNodeEdges:
        ...

    class TestRegisterNodeReflectionBatch:
        ...

    class TestPruneDirectoriesWithoutRoot:
        ...
