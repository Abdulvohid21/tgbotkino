import aiosqlite
from config import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                code TEXT PRIMARY KEY,
                file_id TEXT NOT NULL,
                description TEXT
            )
        ''')
        await db.commit()
        
        # Add a test movie if none exist
        async with db.execute('SELECT COUNT(*) FROM movies') as cursor:
            count = await cursor.fetchone()
            if count[0] == 0:
                # You can replace this with an actual file_id or text
                await db.execute('INSERT INTO movies (code, file_id, description) VALUES (?, ?, ?)', 
                                 ("100", "test_file_id_or_link_here", "Test Kino (100-kod)"))
                await db.commit()

async def get_movie(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT file_id, description FROM movies WHERE code = ?', (code,)) as cursor:
            return await cursor.fetchone()

async def add_movie(code: str, file_id: str, description: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('INSERT OR REPLACE INTO movies (code, file_id, description) VALUES (?, ?, ?)', 
                         (code, file_id, description))
        await db.commit()

async def delete_movie(code: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('DELETE FROM movies WHERE code = ?', (code,))
        await db.commit()
        return cursor.rowcount > 0
