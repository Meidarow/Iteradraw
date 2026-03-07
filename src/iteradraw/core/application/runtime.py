from iteradraw.core.domain.models.folder import Folder
from iteradraw.core.infrastructure.buses.command_bus import CommandBus


class ApplicationRuntime:

    def __init__(self, command_bus: CommandBus, ):
        pass

    def start(self):
        pass

    def shutdown(self):
        pass

# Command API

    def next_timed_slide(self):
        pass

    def previous_timed_slide(self):
        pass

    def next_slide(self):
        pass

    def previous_slide(self):
        pass

# Folder Command Wrappers

    def add_folder(self, folder: Folder):
        pass
    def delete_folder(self, folder: Folder):
        pass
    def rename_folderset(self):
        pass
    def add_folderset(self, folder: Folder):
        pass
    def delete_folderset(self, folder: Folder):
        pass
    def set_folderset_enabled(self, folder: Folder):
        pass
    def set_all_folders_enabled(self, folder: Folder):
        pass

# Query API

    def fetch_session_statistics(self):
        pass

    def fetch_session_images(self):
        pass

    def fetch_tags(self):
        pass