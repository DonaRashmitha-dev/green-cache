#!/usr/bin/env python3
"""Benchmark script for measuring cache performance and hit rates."""

import asyncio
import time

import httpx


async def run_benchmark(
    base_url: str = "http://localhost:8000/api/v1",
):
    """Run benchmark with English paraphrased queries."""

    query_groups = [
        {
            "seed": "What is the capital of France?",
            "paraphrases": [
                "Tell me France's capital city",
                "Which city is the capital of France?",
                "What city serves as France's capital?",
                "Name the capital city of France",
                "Where is the capital of France located?",
            ],
        },
        {
            "seed": "How do I reset my password?",
            "paraphrases": [
                "I forgot my password, help me recover it",
                "Steps to reset my account password",
                "How can I change my password?",
                "I need to recover access to my account",
                "Password recovery process",
            ],
        },
        {
            "seed": "What are the benefits of exercise?",
            "paraphrases": [
                "Why is working out good for you?",
                "Health benefits of physical activity",
                "How does exercise improve health?",
                "Why should I exercise regularly?",
                "Advantages of staying physically active",
            ],
        },
        {
            "seed": "How does photosynthesis work?",
            "paraphrases": [
                "Explain the process of photosynthesis",
                "How do plants make food from sunlight?",
                "What is photosynthesis in simple terms?",
                "How do plants convert light to energy?",
                "Describe photosynthesis process",
            ],
        },
    ]

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Clear cache first
        await client.delete(f"{base_url}/cache")
        print("Cache cleared.")

        print("\nWarming up cache (storing seed queries)...")
        for group in query_groups:
            response = await client.post(
                f"{base_url}/query",
                json={"query": group["seed"], "quality_tier": "standard"},
            )
            print(f"  Stored: {group['seed'][:60]}... (hit: {response.json()['cache_hit']})")

        print("\nBenchmarking English paraphrases...")
        hits = 0
        misses = 0
        total_latency = 0.0

        for group in query_groups:
            print(f"\n  Seed: {group['seed'][:60]}")
            for query in group["paraphrases"]:
                start = time.time()
                response = await client.post(
                    f"{base_url}/query",
                    json={"query": query, "quality_tier": "standard"},
                )
                latency = (time.time() - start) * 1000
                total_latency += latency

                data = response.json()
                hit = data["cache_hit"]
                score = data.get("similarity_score") or 0.0
                if hit:
                    hits += 1
                else:
                    misses += 1

                status = "HIT ✓" if hit else "MISS ✗"
                print(f"    [{status}] score={score:.3f} | {query[:50]}")

        total = hits + misses
        stats_response = await client.get(f"{base_url}/stats")
        stats = stats_response.json()

        impact_response = await client.get(f"{base_url}/impact")
        impact = impact_response.json()

        print(f"\n=== Results ===")
        print(f"Hit rate:     {hits}/{total} = {hits/total:.1%}")
        print(f"Avg latency:  {total_latency / total:.1f}ms")
        print(f"Cache entries:{stats['entries_count']}")
        print(f"Water saved:  {impact['total_water_saved_liters']:.6f} liters")
        print(f"Energy saved: {impact['total_energy_saved_wh']:.4f} Wh")


if __name__ == "__main__":
    asyncio.run(run_benchmark())