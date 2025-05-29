# surf-planner
## start app 
```bash
DB_USER=admin DB_PW=admin uvicorn main:app --reload
```
## recreate database tables 

```bash
cd loader 
DB_USER=admin DB_PW=admin  python transformer.py
```

