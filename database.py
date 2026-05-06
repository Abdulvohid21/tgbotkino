import asyncpg
from config import DATABASE_URL
import logging

async def connect_db():
    try:
        return await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        return None

async def init_db():
    conn = await connect_db()
    if not conn:
        return
        
    try:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                code TEXT PRIMARY KEY,
                file_id TEXT NOT NULL,
                description TEXT
            )
        ''')
        
        # Add a test movie if none exist
        count = await conn.fetchval('SELECT COUNT(*) FROM movies')
        if count == 0:
            await conn.execute('''
                INSERT INTO movies (code, file_id, description) 
                VALUES ($1, $2, $3)
            ''', "100", "test_file_id_or_link_here", "Test Kino (100-kod)")
    finally:
        await conn.close()

async def get_movie(code: str):
    conn = await connect_db()
    if not conn: return None
    try:
        row = await conn.fetchrow('SELECT file_id, description FROM movies WHERE code = $1', code)
        if row:
            return dict(row)
        return None
    finally:
        await conn.close()

async def add_movie(code: str, file_id: str, description: str = ""):
    conn = await connect_db()
    if not conn: return
    try:
        await conn.execute('''
            INSERT INTO movies (code, file_id, description) 
            VALUES ($1, $2, $3)
            ON CONFLICT (code) 
            DO UPDATE SET file_id = EXCLUDED.file_id, description = EXCLUDED.description
        ''', code, file_id, description)
    finally:
        await conn.close()

async def delete_movie(code: str) -> bool:
    conn = await connect_db()
    if not conn: return False
    try:
        result = await conn.execute('DELETE FROM movies WHERE code = $1', code)
        # result returns string like "DELETE 1" or "DELETE 0"
        return result != "DELETE 0"
    finally:
        await conn.close()
