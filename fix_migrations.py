"""
fix_migrations.py  — run this ONCE from your project root:
    python fix_migrations.py

What it does:
  1. Removes ALL studapp migration records from django_migrations table
  2. Creates the Task and LeaveRequest tables directly via SQL
  3. Records the new migration as applied
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studproject.settings')
django.setup()

from django.db import connection

print("=" * 60)
print("  Migration Fix Script")
print("=" * 60)

with connection.cursor() as cursor:

    # ── Step 1: Remove all studapp migration records ──────────────
    print("\n[1] Clearing old studapp migration records...")
    cursor.execute("DELETE FROM django_migrations WHERE app = 'studapp'")
    print("    Done.")

    # ── Step 2: Check which tables already exist ───────────────────
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {row[0] for row in cursor.fetchall()}
    print(f"\n[2] Existing tables: {sorted(existing_tables)}")

    # ── Step 3: Create Task table if not exists ────────────────────
    if 'studapp_task' not in existing_tables:
        print("\n[3] Creating studapp_task table...")
        cursor.execute("""
            CREATE TABLE "studapp_task" (
                "id"          integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "title"       varchar(200) NOT NULL,
                "description" text NOT NULL,
                "due_date"    date NOT NULL,
                "priority"    varchar(10) NOT NULL,
                "status"      varchar(15) NOT NULL,
                "assigned_on" datetime NOT NULL,
                "student_id"  integer NOT NULL
                    REFERENCES "studapp_student" ("id")
                    DEFERRABLE INITIALLY DEFERRED
            )
        """)
        cursor.execute("""
            CREATE INDEX "studapp_task_student_id_idx"
            ON "studapp_task" ("student_id")
        """)
        print("    studapp_task created ✅")
    else:
        print("\n[3] studapp_task already exists, skipping.")

    # ── Step 4: Create LeaveRequest table if not exists ────────────
    if 'studapp_leaverequest' not in existing_tables:
        print("\n[4] Creating studapp_leaverequest table...")
        cursor.execute("""
            CREATE TABLE "studapp_leaverequest" (
                "id"           integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "leave_type"   varchar(20) NOT NULL,
                "from_date"    date NOT NULL,
                "to_date"      date NOT NULL,
                "reason"       text NOT NULL,
                "status"       varchar(10) NOT NULL,
                "applied_on"   datetime NOT NULL,
                "admin_remark" text NOT NULL,
                "student_id"   integer NOT NULL
                    REFERENCES "studapp_student" ("id")
                    DEFERRABLE INITIALLY DEFERRED
            )
        """)
        cursor.execute("""
            CREATE INDEX "studapp_leaverequest_student_id_idx"
            ON "studapp_leaverequest" ("student_id")
        """)
        print("    studapp_leaverequest created ✅")
    else:
        print("\n[4] studapp_leaverequest already exists, skipping.")

    # ── Step 5: Record the migration as applied ────────────────────
    print("\n[5] Recording migrations as applied...")
    from django.utils import timezone
    now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

    # Check if studapp already had an initial migration in the original project
    # We need to fake that one too so Django doesn't try to re-run it
    cursor.execute(
        "INSERT OR IGNORE INTO django_migrations (app, name, applied) VALUES (?, ?, ?)",
        ['studapp', '0001_new_features', now]
    )
    print("    Recorded 0001_new_features ✅")

print("\n" + "=" * 60)
print("  ✅ ALL DONE! Now run:  python manage.py runserver")
print("=" * 60 + "\n")
