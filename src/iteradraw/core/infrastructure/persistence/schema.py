SCHEMA = """
CREATE TABLE IF NOT EXISTS foldersets (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
    
CREATE TABLE IF NOT EXISTS directories (
    dir_id INTEGER NOT NULL PRIMARY KEY,
    dir_name TEXT NOT NULL,
    crawl_time INT NOT NULL,
    mod_time INT NOT NULL
);
    
CREATE TABLE IF NOT EXISTS rootfolders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    folderset_id INT NOT NULL,
    UNIQUE (path, folderset_id),
    FOREIGN KEY(folderset_id) REFERENCES foldersets(id)
    ON DELETE CASCADE,
    FOREIGN KEY (id) REFERENCES directories(dir_id)
);
    
CREATE TABLE IF NOT EXISTS folders_closure (
    ancestor_id INT NOT NULL,
    descendant_id INT NOT NULL,
    depth INT NOT NULL,
    PRIMARY KEY (ancestor_id, descendant_id),
    FOREIGN KEY (ancestor_id) REFERENCES directories(dir_id),
    FOREIGN KEY (descendant_id) REFERENCES directories(dir_id)
);
    
CREATE TABLE IF NOT EXISTS images (
    image_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id INTEGER NOT NULL,
    FOREIGN KEY (parent_id) REFERENCES discovered_folders(dir_id)
    ON DELETE CASCADE
);
"""