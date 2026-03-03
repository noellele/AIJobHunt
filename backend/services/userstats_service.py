from datetime import datetime, timezone


async def recalculate_top_missing_skill_for_user(db, user_oid):
    pipeline = [
        {"$match": {"user_id": user_oid}},
        {"$unwind": "$missing_skills"},
        {
            "$group": {
                "_id": "$missing_skills",
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]

    cursor = await db.job_matches.aggregate(pipeline)
    results = await cursor.to_list(length=1)

    top_skill = results[0]["_id"] if results else None

    await db.user_stats.update_one(
        {"user_id": user_oid},
        {
            "$set": {
                "top_missing_skill": top_skill,
                "last_calculated": datetime.now(timezone.utc),
            }
        },
        upsert=True
    )
