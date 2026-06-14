import asyncio, httpx

async def test():
    async with httpx.AsyncClient(timeout=30) as c:
        queries = [
            "What is photosynthesis?",
            "Explain photosynthesis",
            "How does photosynthesis work?",
            "Describe photosynthesis process",
            "What is the capital of France?",
            "France capital city name",
            "Which city is France capital?",
            "How do I reset my password?",
            "Password reset steps",
            "How to change my password?",
            "What are benefits of exercise?",
            "Why exercise is good for health?",
            "Health benefits of working out?",
        ]
        hits = 0
        for q in queries:
            r = await c.post("http://localhost:8000/api/v1/query", json={"query": q, "quality_tier": "standard", "user_id": "alice"})
            d = r.json()
            if d["cache_hit"]:
                hits += 1
            print(("HIT" if d["cache_hit"] else "MISS") + " | " + q[:45])
        await c.get("http://localhost:8000/api/v1/stats")
        print("Hit rate this batch: " + str(round(hits/len(queries)*100, 1)) + "%")

asyncio.run(test())
