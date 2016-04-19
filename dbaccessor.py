from pymongo import MongoClient


class DBAccessor:
    def __init__(self, db='zhihu', collection='users_test3'):
        self.collection = MongoClient()[db][collection]

    def find(self, criteria_dict=None, column=None):
        return self.collection.find(criteria_dict, column)

    def delete(self, criteria_dict=None):
        num = self.get_user_number()
        if raw_input('Going to delete {} record, confirm? (y/n)'.format(num)).startswith('y'):
            return self.collection.delete_many(criteria_dict)
        else:
            print 'delete canceled'

    def insert(self, user_dict):
        self.collection.insert(user_dict)

    def get_user_number(self):
        return self.collection.count()

if __name__ == "__main__":
    db = DBAccessor(collection='users_test3')
    # print db.get_user_number()

    # print len(list(db.find({}, {'_id': 0, 'user_hash': 1})))
    # print list(cursor)
    print db.delete({}).deleted_count