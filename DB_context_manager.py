from mysql.connector import connect


class UseDatabase:
    def __init__(self, config: dict) -> None:
        self.configuration = config

    def __enter__(self) -> 'cursor':
        self.connector = connect(**self.configuration)
        self.cursor = self.connector.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_trace) -> None:
        self.connector.commit()
        self.cursor.close()
        self.connector.close()
