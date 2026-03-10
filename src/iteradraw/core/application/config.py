
class ApplicationConfiguration:
    def __init__(self):
        self.db_path = ":memory:"
        self.crawler_batch_size = 5000