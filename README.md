# 🧠 Elasticsearch Scroll Exporter

A Python script to export all documents from an Elasticsearch index using the **Scroll API**.  
It retrieves documents in batches and saves them as JSON files — perfect for **backups, migrations**, or **offline data analysis**.

---

## 🚀 Features
- Connects securely to your Elasticsearch cluster  
- Uses the **Scroll API** for efficient large data exports  
- Exports all documents from an index  
- Saves data in multiple JSON files (batches)  
- Cleans up the scroll context after export  

---

## ⚙️ Requirements

- Python **3.8+**
- Elasticsearch Python client

Install dependencies:

```bash
pip install -r requirements.txt
```
---

## 📘 Usage
1. **Edit the Configuration**

Open the Script (`scroll_exporter.py`) and update these fields:
```python
    ES_HOST = "https://your-elastic-host.com"
    ES_USER = "elastic"
    ES_PASS = "your-password"
    INDEX_NAME = "your-index-name"
```
2. **Run the Script**

```bash
python scroll_exporter.py

```
3. **Exported Files**

The exported JSON files will be saved in the `es_exports/` folder:

```txt
es_exports/
├── your_index_part1.json
├── your_index_part2.json
└── ...
```

## 📄 Example Output

```yaml
✅ Connected to Elasticsearch 8.x
📊 Total documents to export: 272,261
📦 Exported 1000/272261 documents so far...
💾 Saved 1000 docs to es_exports/staging_author_es_part1.json
✅ Export complete. Total docs exported: 272261
🧹 Cleared scroll context.

```


