#!/usr/bin/env python3
"""
Demo script to show caching performance improvement

Run this inside Docker container:
docker-compose exec backend python test_caching_demo.py
"""

import asyncio
from datetime import date
from app.config.database import get_async_session
from app.core.cache import CacheService
from app.models.tip import Tip, DifficultyLevel
from app.services.tip import TipService
import time


async def main():
    """Test caching performance"""
    print("🧪 Testing Redis Caching Performance\n")

    # Setup
    cache = CacheService()
    await cache.connect()

    async for db in get_async_session():
        # Create test tip
        today = date.today()

        # Check if tip exists
        existing_tip = await db.execute(
            f"SELECT * FROM tips WHERE publish_date = '{today}' LIMIT 1"
        )
        if not existing_tip.first():
            tip = Tip(
                title="Test Caching Tip",
                content="This tip is used to test Redis caching performance. " * 5,
                difficulty=DifficultyLevel.BEGINNER,
                category=["performance"],
                publish_date=today,
                is_active=True,
            )
            db.add(tip)
            await db.commit()
            print("✅ Created test tip")

        # Test 1: Without cache
        print("\n📊 Test 1: Without Cache (Direct DB Access)")
        service_no_cache = TipService()
        start = time.time()
        tip1 = await service_no_cache.get_daily_tip(db, today)
        elapsed_no_cache = (time.time() - start) * 1000
        print(f"   Time: {elapsed_no_cache:.2f}ms")

        # Test 2: With cache (first call - MISS)
        print("\n📊 Test 2: With Cache (First Call - Cache MISS)")
        service_with_cache = TipService(cache=cache)
        start = time.time()
        tip2 = await service_with_cache.get_daily_tip(db, today)
        elapsed_cache_miss = (time.time() - start) * 1000
        print(f"   Time: {elapsed_cache_miss:.2f}ms")

        # Test 3: With cache (second call - HIT)
        print("\n📊 Test 3: With Cache (Second Call - Cache HIT)")
        start = time.time()
        tip3 = await service_with_cache.get_daily_tip(db, today)
        elapsed_cache_hit = (time.time() - start) * 1000
        print(f"   Time: {elapsed_cache_hit:.2f}ms")

        # Calculate improvement
        improvement = ((elapsed_no_cache - elapsed_cache_hit) / elapsed_no_cache) * 100
        print(f"\n🚀 Performance Improvement: {improvement:.1f}%")
        print(f"   Speedup: {elapsed_no_cache / elapsed_cache_hit:.1f}x faster")

        # Cleanup
        await cache.disconnect()
        break


if __name__ == "__main__":
    asyncio.run(main())
