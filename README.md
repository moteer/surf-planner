# surf-planner
## start app 
```bash
DB_USER=admin DB_PW=admin uvicorn main:app --reload
```
## load new csv and transform it (add csv path before)

```bash
cd loader 
DB_USER=admin DB_PW=admin  python transformer.py
```

