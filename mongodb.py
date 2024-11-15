import motor.motor_asyncio


class mongo_connection:

    client, db = None, None

    token_list = []


    async def connect_server(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://127.0.0.1:27017/?retryWrites=true&w=majority',
                                                             serverSelectionTimeoutMS=5000)
        self.db = self.client["kolyaBot"]
        async for token in self.get_token_list():
            self.token_list.append(token.get("token_id"))

    async def add_token(self, token):
        self.db.tokens.insert_one({"token_id": token})
        self.token_list.append(token)

    async def delete_token(self, token):
        self.db.tokens.delete_one({"token_id": token})
        self.token_list.remove(token)

    def get_token_list(self):
        token_list = self.db.tokens.find()
        return token_list

    def del_market_cap(self):
        self.db.market_cap.delete_many({})

    async def change_market_cap(self, new_market_cap):
        self.db.market_cap.insert_one({"market_cap": new_market_cap})

    async def get_market_cap(self):
        return await self.db.market_cap.find_one({})


mongo_conn = mongo_connection()