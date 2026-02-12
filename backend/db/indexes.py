from backend.db.mongo import get_db


async def ensure_indexes():
    db = get_db()

    # Prevent duplicate interaction types for same user/job
    await db.user_job_interactions.create_index(
        [
            ("user_id", 1),
            ("job_id", 1),
            ("interaction_type", 1),
        ],
        unique=True,
        name="uniq_user_job_interaction",
    )

    # Fast lookup of all interactions for user
    await db.user_job_interactions.create_index(
        [("user_id", 1)],
        name="idx_interactions_user",
    )

    # Fast lookup of job interactions
    await db.user_job_interactions.create_index(
        [("job_id", 1)],
        name="idx_interactions_job",
    )

    # User Stats
    await db.user_stats.create_index(
        [("user_id", 1)],
        unique=True,
        name="uniq_userstats_user",
    )

    # Saved Searches
    await db.saved_searches.create_index(
        [("user_id", 1)],
        name="idx_savedsearch_user",
    )

    # Users
    await db.users.create_index(
        [("email", 1)],
        unique=True,
        name="uniq_user_email",
    )

    # Jobs
    await db.jobs.create_index(
        [("external_id", 1)],
        unique=True,
        name="uniq_external_job",
    )

    # Job Matches
    await db.job_matches.create_index(
        [("user_id", 1), ("job_id", 1)],
        unique=True,
        name="uniq_job_match_user_job",
    )
    await db.job_matches.create_index(
        [("user_id", 1)],
        name="idx_job_matches_user",
    )
    await db.job_matches.create_index(
        [("job_id", 1)],
        name="idx_job_matches_job",
    )
    await db.job_matches.create_index(
        [("relevancy_score", 1)],
        name="idx_job_matches_score",
    )
