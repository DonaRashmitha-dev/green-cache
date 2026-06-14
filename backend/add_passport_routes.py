lines = open("src/api/routes.py", "r", encoding="utf-8").readlines()

new_endpoints = '''
@router.get("/passport/{user_id}")
async def get_user_passport(user_id: str) -> dict:
    passport = get_passport()
    data = passport.get(user_id)
    if not data:
        return {"user_id": user_id, "message": "No data yet", "total_queries": 0}
    return data


@router.get("/passport")
async def get_leaderboard() -> dict:
    passport = get_passport()
    return {"leaderboard": passport.leaderboard(top_n=10), "total_users": len(passport._users)}
'''

# Insert before last route (health check)
for i, line in enumerate(lines):
    if '@router.get("/health")' in line:
        lines.insert(i, new_endpoints)
        break

open("src/api/routes.py", "w", encoding="utf-8").writelines(lines)
print("Passport endpoints added!")
