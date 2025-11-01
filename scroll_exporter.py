
"""
Elasticsearch Scroll Exporter
-----------------------------
This script connects to an Elasticsearch cluster and exports all documents from a specified index
using the scroll API. It retrieves data in batches, saves each batch as a JSON file, and clears the
scroll context after completion—ideal for full index backups, migrations, or offline analysis.
"""



from elasticsearch import Elasticsearch
import json
import os
import sys

# === Configuration ===

ES_HOST = os.getenv("ES_HOST")
ES_USER = os.getenv("ES_USER")
ES_PASS = os.getenv("ES_PASS")

INDEX_NAME = "your_index_name"        # Index name

SCROLL_TIMEOUT = "5m"                 # How long each scroll context is kept alive
BATCH_SIZE = 1000                     # Number of docs per batch
OUTPUT_DIR = "es_exports"             # Output directory

# === Setup Connection ===
try:
    es = Elasticsearch(
        ES_HOST,
        basic_auth=(ES_USER, ES_PASS)
    )

    if not es.ping():
        print(f"❌ Failed to connect to Elasticsearch at {ES_HOST}")
        sys.exit(1)
    else:
        info = es.info()
        print(f"✅ Connected to Elasticsearch {info['version']['number']} at {ES_HOST}")
except Exception as e:
    print(f"❌ Connection error: {e}")
    sys.exit(1)

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Initialize scroll ===
print(f"📥 Starting scroll export from index: {INDEX_NAME}")
try:
    response = es.search(
        index=INDEX_NAME,
        scroll=SCROLL_TIMEOUT,
        body={
            "size": BATCH_SIZE,
            "query": {
                "match_all": {}
            }
        }
    )
except Exception as e:
    print(f"❌ Search failed: {e}")
    sys.exit(1)

# scroll_id = response.get('_scroll_id')
# hits = response['hits']['hits']
# total_docs = response['hits']['total']['value'] if isinstance(response['hits']['total'], dict) else response['hits']['total']
# print(f"📊 Total documents to export: {total_docs}")


scroll_id = response.get('_scroll_id')
hits = response['hits']['hits']

print(f"🧪 Initial search got {len(hits)} documents")

total_docs = response['hits']['total']['value'] if isinstance(response['hits']['total'], dict) else response['hits']['total']
print(f"📊 Total documents to export: {total_docs}")


file_count = 1
doc_counter = 0

def write_to_file(docs, file_num):
    """Writes documents to a JSON file as a proper array"""
    file_path = os.path.join(OUTPUT_DIR, f"{INDEX_NAME}_part{file_num}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    print(f"💾 Saved {len(docs)} docs to {file_path}")

# === Scroll loop ===
buffer = []

try:
    while hits:
        for doc in hits:
            buffer.append(doc)  # Save full document (_id, _index, _source)
            doc_counter += 1

            if len(buffer) >= BATCH_SIZE:
                write_to_file(buffer, file_count)
                print(f"📦 Exported {doc_counter}/{total_docs} documents so far...")
                file_count += 1
                buffer = []

        if not scroll_id:
            print("⚠️ No scroll_id returned, stopping.")
            break

        response = es.scroll(scroll_id=scroll_id, scroll=SCROLL_TIMEOUT)
        scroll_id = response.get('_scroll_id')
        hits = response['hits']['hits'] if response and 'hits' in response else []

    # Write any remaining documents
    if buffer:
        write_to_file(buffer, file_count)
        print(f"📦 Exported {doc_counter}/{total_docs} documents so far...")

    print(f"\n✅ Export complete. Total docs exported: {doc_counter}")

    # Clear scroll context
    try:
        es.clear_scroll(scroll_id=scroll_id)
        print("🧹 Cleared scroll context.")
    except Exception as e:
        print(f"⚠️ Failed to clear scroll: {e}")

except Exception as err:
    print(f"❌ Error during scroll: {err}")
