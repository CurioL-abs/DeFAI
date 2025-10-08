#!/usr/bin/env python3
import asyncio
import sys

async def test():
    print("\n🔍 Quick PostgreSQL Connection Test")
    print("="*50)
    
    try:
        import asyncpg
    except ImportError:
        print("\n❌ asyncpg not installed")
        print("💡 Install it: pip install asyncpg")
        return False
    
    try:
        print("📡 Connecting to database...")
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='password',
            database='defai_agents'
        )
        
        print("✅ Connected successfully!")
        
        version = await conn.fetchval('SELECT version()')
        print(f"✅ PostgreSQL: {version.split(',')[0]}")
        
        db = await conn.fetchval('SELECT current_database()')
        print(f"✅ Database: {db}")
        
        result = await conn.fetchval('SELECT 1 + 1')
        print(f"✅ Test query: 1 + 1 = {result}")
        
        await conn.close()
        print("\n" + "="*50)
        print("🎉 Database is ready!")
        print("="*50)
        
        print("\n💡 Next steps:")
        print("   Run full test: python3 test_db_integration.py")
        print("   Or use script: bash scripts/test-db.sh")
        
        return True
        
    except asyncpg.PostgresConnectionError as e:
        print(f"\n❌ Cannot connect to PostgreSQL")
        print(f"   Error: {e}")
        print("\n💡 Make sure PostgreSQL is running:")
        print("   docker-compose up -d postgres")
        print("   Wait 10 seconds then try again")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test())
    sys.exit(0 if result else 1)

