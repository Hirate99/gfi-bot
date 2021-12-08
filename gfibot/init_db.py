import os
import json
import pymongo
import logging
import gfibot


if __name__ == "__main__":
    mongo_url = gfibot.CONFIG["mongodb"]["url"]
    db_name = gfibot.CONFIG["mongodb"]["db"]
    collections = gfibot.CONFIG["mongodb"]["collections"].values()
    logging.info("MongoDB URL: %s, DB Name: %s", mongo_url, db_name)

    with pymongo.MongoClient(mongo_url) as client:
        db = client[db_name]
        existing_collections = db.list_collection_names()

        for c in collections:
            if c["name"] in existing_collections:
                logging.warning(
                    "Collection %s already exists (%d documents), skipping",
                    c["name"],
                    db[c["name"]].count_documents(filter={}),
                )
                logging.info("Please drop all collections before re-initializing")
                continue

            logging.info("Initializing Collection: %s", c)
            with open(gfibot.BASE_DIR / "schemas" / (c["name"] + ".json"), "r") as f:
                schema = json.load(f)
            db.create_collection(c["name"], validator={"$jsonSchema": schema})
            db[c["name"]].create_index(
                [(i, pymongo.ASCENDING) for i in c["index"]], unique=True
            )

    logging.info("Finish!")