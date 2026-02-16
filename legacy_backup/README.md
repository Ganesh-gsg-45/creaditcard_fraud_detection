# Legacy Flask Application

This folder contains the **old Flask-based API** that has been replaced by the new **FastAPI + Streamlit** application.

## Files

- `app_flask.py` - Original Flask API with HTML documentation
- `pipeline_old/` - Old pipeline directory (if existed)

## Why Replaced?

The new version provides:
- ✅ Better performance (FastAPI)
- ✅ Interactive UI (Streamlit)
- ✅ 3-tier decision logic (vs 2-tier)
- ✅ Automatic validation (Pydantic)
- ✅ Auto-generated API docs (Swagger)
- ✅ Better error handling
- ✅ Modern architecture

## Using the Old Version

If you need to run the old Flask version:

```bash
python app_flask.py
```

Then visit: http://localhost:5000

---

**Recommendation:** Use the new FastAPI + Streamlit version instead!
