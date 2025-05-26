# surf-planner
## start app 
```bash
DB_USER=admin DB_PW=admin uvicorn main:app --reload

## recreate database tables 
```bash
DB_USER=admin DB_PW=admin python create_db.py


