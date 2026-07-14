import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import text
from src.resources.database import DatabaseManager

load_dotenv()

async def main():
    dsn = os.getenv("POSTGRES_DSN")
    print(f"Connecting to: {dsn}")
    db = DatabaseManager(dsn)
    async for session in db.get_session():
        # Query columns
        query_cols = text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'agh' AND table_name = 'aip_pacientes'
        """)
        res = await session.execute(query_cols)
        cols = res.all()
        print("\nColunas encontradas:")
        for col in cols:
            print(f"  {col[0]} ({col[1]})")
            
        # Also query one sample patient to see the data
        query_sample = text("SELECT * FROM agh.aip_pacientes LIMIT 1")
        res_sample = await session.execute(query_sample)
        sample = res_sample.mappings().first()
        if sample:
            print("\nExemplo de registro:")
            for k, v in sample.items():
                print(f"  {k}: {v}")
        break

if __name__ == "__main__":
    asyncio.run(main())
