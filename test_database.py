#!/usr/bin/env python3
import asyncio
import asyncpg
import sys
import os
from datetime import datetime

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/defai_agents"
)

async def test_connection():
    print("=" * 60)
    print("🔍 DeFAI Database Connection Test")
    print("=" * 60)
    print(f"📍 Database URL: {DATABASE_URL.replace('password', '****')}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        print("\n1️⃣  Testing database connection...")
        conn = await asyncpg.connect(DATABASE_URL)
        print("   ✅ Connection established")
        
        print("\n2️⃣  Testing query execution...")
        version = await conn.fetchval('SELECT version()')
        print(f"   ✅ PostgreSQL version: {version.split(',')[0]}")
        
        print("\n3️⃣  Testing database existence...")
        db_name = await conn.fetchval('SELECT current_database()')
        print(f"   ✅ Connected to database: {db_name}")
        
        print("\n4️⃣  Testing table creation...")
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        print("   ✅ Test table created")
        
        print("\n5️⃣  Testing data insertion...")
        await conn.execute(
            "INSERT INTO test_table (name) VALUES ($1)",
            "test_connection"
        )
        print("   ✅ Test data inserted")
        
        print("\n6️⃣  Testing data retrieval...")
        rows = await conn.fetch("SELECT * FROM test_table LIMIT 5")
        print(f"   ✅ Retrieved {len(rows)} row(s)")
        for row in rows:
            print(f"      - ID: {row['id']}, Name: {row['name']}, Created: {row['created_at']}")
        
        print("\n7️⃣  Cleaning up test table...")
        await conn.execute("DROP TABLE IF EXISTS test_table")
        print("   ✅ Test table cleaned up")
        
        await conn.close()
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - Database is ready!")
        print("=" * 60)
        return True
        
    except asyncpg.PostgresConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure PostgreSQL container is running:")
        print("      docker-compose up -d postgres")
        print("   2. Check if port 5432 is available:")
        print("      lsof -i :5432")
        print("   3. Verify database credentials")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"   Type: {type(e).__name__}")
        return False

async def test_with_sqlalchemy():
    print("\n" + "=" * 60)
    print("🔍 Testing SQLAlchemy Async Connection")
    print("=" * 60)
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        engine = create_async_engine(
            DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
            echo=False
        )
        
        print("\n1️⃣  Creating SQLAlchemy engine...")
        print("   ✅ Engine created")
        
        print("\n2️⃣  Testing connection...")
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()
            print(f"   ✅ Query result: {value}")
        
        await engine.dispose()
        print("\n✅ SQLAlchemy connection test passed!")
        return True
        
    except ImportError as e:
        print(f"\n⚠️  SQLAlchemy not installed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ SQLAlchemy test failed: {e}")
        return False

def main():
    print("\n🚀 Starting Database Tests...\n")
    
    loop = asyncio.get_event_loop()
    test1 = loop.run_until_complete(test_connection())
    test2 = loop.run_until_complete(test_with_sqlalchemy())
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    print(f"Basic Connection Test: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"SQLAlchemy Test:       {'✅ PASS' if test2 else '⚠️  SKIP'}")
    print("=" * 60)
    
    if test1 and test2:
        print("\n🎉 Database setup is complete and working!")
        sys.exit(0)
    elif test1:
        print("\n⚠️  Database connection works, but SQLAlchemy needs setup")
        sys.exit(0)
    else:
        print("\n❌ Database setup needs attention")
        sys.exit(1)

if __name__ == "__main__":
    main()

