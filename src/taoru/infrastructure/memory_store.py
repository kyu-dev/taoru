import sqlite3

from langgraph.store.sqlite import SqliteStore

conn = sqlite3.connect("memory_store.db", check_same_thread=False, isolation_level=None)
store = SqliteStore(conn)
store.setup()
