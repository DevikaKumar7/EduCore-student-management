========================================================
  SETUP INSTRUCTIONS — New Features Migration Fix
========================================================

Your existing database already has Student + Attendance tables.
The new migration only adds Task and LeaveRequest tables.

Follow these steps IN ORDER:

--------------------------------------------------------------
STEP 1 — Delete all files inside your migrations folder
         (keep __init__.py, delete everything else)
--------------------------------------------------------------
Your migrations folder is:
  studapp/migrations/

Delete any existing .py files EXCEPT __init__.py
Then copy the new 0001_new_features.py into that folder.

--------------------------------------------------------------
STEP 2 — Tell Django your existing tables are already created
         (fake-initial so Django doesn't try to recreate them)
--------------------------------------------------------------

Run this command:

  python manage.py migrate studapp --fake-initial

This tells Django: "pretend the initial migration already ran"
so it won't try to recreate Student/Attendance tables.

--------------------------------------------------------------
STEP 3 — Run normal migrate to create the 2 NEW tables
--------------------------------------------------------------

  python manage.py migrate

This will create:
  ✅ studapp_task
  ✅ studapp_leaverequest

--------------------------------------------------------------
STEP 4 — Run the server
--------------------------------------------------------------

  python manage.py runserver

Then open: http://127.0.0.1:8000/

--------------------------------------------------------------
NEW URLS available after setup:
--------------------------------------------------------------
  /tasks/              → Task list (admin)
  /tasks/assign/       → Assign task to student
  /leaves/             → Leave requests list
  /leaves/apply/       → Submit leave request
  /leaves/<id>/action/ → Approve or Reject a leave

========================================================
IF YOU STILL GET ERRORS — Nuclear Option (fresh DB):
========================================================
If nothing works, just delete db.sqlite3 and start fresh:

  1. Delete db.sqlite3
  2. Delete all files in migrations/ except __init__.py
  3. Copy 0001_new_features.py into migrations/
  4. Run: python manage.py migrate
  5. Run: python manage.py createsuperuser
  6. Run: python manage.py runserver

========================================================
