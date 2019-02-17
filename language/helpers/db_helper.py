from pymongo import MongoClient
import pymongo
import subprocess
import os
import bson
import re


class MongoDBConnect(object):
    """Connect to a database Connection Class."""

    def __init__(
            self,
            host="mongo",
            port=27017,
            db_name="",
            username="",
            password=""
    ):
        """

        :param host:
        :param port:
        :param dbname:
        :param username:
        :param password:
        """
        self.host = host
        self.port = port
        self.db_name = db_name
        self.username = username
        self.password = password
        self.client = MongoClient(
            self.host,
            self.port,
            username=self.username,
            password=self.password,
            # authSource=self.db_name,
            # authMechanism='SCRAM-SHA-256'
        )
        self.exception_count = 0
        self.db = self.client[self.db_name]

    @staticmethod
    def drop_database(host="localhost", port=27017, db_name=""):
        """

        :return:
        """

        db = MongoClient(host, port)

        # drop database
        db.drop_database(db_name)

    @staticmethod
    def check_database_exists(host="localhost", port=27017, db_name=""):
        """

        :return:
        """

        db = MongoClient(host, port)

        dbnames = db.list_database_names()
        if db_name in dbnames:
            return True
        return False

    def insert_data(self, collection_name="item", insert_data={}):
        """Create a new schema request."""
        try:
            inserted_object = self.db[collection_name].insert_one(insert_data)
            return inserted_object.inserted_id
        except pymongo.errors.WriteError as e:
            print(str(e))
            # print("pymongo.errors.WriteError: can't map file memory - mongo requires 64 bit build for larger datasets")

    def update_data(self, collection_name="item", update_condition={}, update_data={}, upsert=False):
        """Create a new schema request."""
        return self.db[collection_name].update_one(
            update_condition,
            {"$set": update_data},
            upsert=upsert
        )

    def delete_data(self, collection_name="item", condition={}):
        """Create a new schema request."""
        return self.db[collection_name].delete_one(
            condition
        )

    def update_many_data(self, collection_name="item", update_condition={}, update_data={}, upsert=False):
        """Create a new schema request."""
        updated = self.db[collection_name].update_many(
            update_condition,
            {"$set": update_data},
            upsert=upsert
        )
        return updated

    def get_data_count(self, collection_name="item"):
        """

        :param collection_name:
        :return:
        """
        return self.db[collection_name].count({})

    def import_collection_from_csv(self, collection_name, file_with_full_path, fields, delimiter= ','):
        """

        :param file_with_full_path:
        :return:
        """

        file_type = "csv"
        if delimiter == ',':
            file_type = 'csv'

        elif delimiter == '|':
            file_type = 'csv'

        elif delimiter == '\t':
            file_type = 'tsv'

        fields_strigifield = self.convert_to_string(fields)

        import_command = "mongoimport --db=" + \
                         self.db_name.replace(' ','') + \
                         " --collection=" + \
                         collection_name.replace(".", "dot") + \
                         " --username='" + \
                         self.username + \
                         "' --password='" + \
                         "' --file='" + file_with_full_path + \
                         "' --type='" + str(file_type) + "' "

        if file_type == 'csv':
            import_command += " --columnsHaveTypes "
            import_command += " --fields='" + fields_strigifield + "' "

        elif file_type == 'tsv':
            import_command += " --headerline"

        print(import_command)
        subprocess.call(import_command, shell=True, stdout=open(os.devnull, 'wb'))

        self.remove_header_saved_as_data(
            collection_name.replace(".", "dot"),
            fields
        )

    def aggregate_generic(self, collection, condition):
        """

        :param collection:
        :param query:
        :return:
        """
        return self.db[collection].aggregate(condition, allowDiskUse=True)

    def aggegerate_collection(self, collection):
        """
        Creates collection "collection_products". This contains products belonging to a collection.
        :param collection:
        :return:
        """
        self.drop_collection("collection_products")
        query = [
            {'$group': {'_id':'$collection_id',
                        'products': {'$addToSet': {'id':'$product_id'}}}},
            # {'$sort': {'sort_value': -1}},
            {'$out': "collection_products"}
        ]
        return self.db[collection].aggregate(query, allowDiskUse=True)

    def drop_collection(self, collection_name=""):
        """

        :param collection_name:
        :return:
        """
        ''' Drop Collection. '''
        self.db[collection_name].drop()

    def find(self, collection_name="", condition={}, projection={}):
        """

        :param collection_name:
        :param condition:
        :param projection:
        :return:
        """

        ''' Search Collection. '''
        if projection.keys():
            return self.db[collection_name].find(condition, projection)
        else:
            return self.db[collection_name].find(condition)

    def find_one(self, collection_name="", condition={}, projection={}):
        """

        :param collection_name:
        :param condition:
        :param projection:
        :return:
        """

        '''Search only one match case'''
        if projection.keys():
            return self.db[collection_name].find_one(condition, projection)
        else:
            return self.db[collection_name].find_one(condition)

    def drop_data(self, collection_name="", condition={}):
        """

        :param collection_name:
        :param condition:
        :return:
        """

        # remove data
        return self.db[collection_name].remove(condition)

    def get_unique_data(self, collection_name="", condition={}, column="", projection={}):
        """

        :param collection_name:
        :param column:
        :return:
        """
        if projection.keys():
            return self.db[collection_name].find(condition, projection).distinct(column)
        else:
            return self.db[collection_name].find(condition).distinct(column)


    def close_connection(self):
        """

        :return:
        """
        self.client.close()
