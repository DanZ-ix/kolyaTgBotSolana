import motor.motor_asyncio


class mongo_connection:

    client, db = None, None



    async def connect_server(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://127.0.0.1:27017/?retryWrites=true&w=majority',
                                                             serverSelectionTimeoutMS=5000)
        self.db = self.client["kolyaBot"]

    async def add_acc(self, acc):
        self.db.accs.insert_one({"acc": acc})


    async def delete_acc(self, acc):
        self.db.accs.delete_one({"acc": acc})


    def get_acc_list(self):
        acc_list = self.db.accs.find()
        return acc_list


mongo_conn = mongo_connection()