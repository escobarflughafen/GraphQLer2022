import { DataSource } from "typeorm";
import { user } from "./Entities/user";
import { wallet } from "./Entities/wallet";
import { currency } from "./Entities/currency";
import { location } from "./Entities/location";
import { transaction } from "./Entities/transaction";
import { credential } from "./Entities/credential";

const SqliteDataSource = new DataSource({
    type: "sqlite",
    database: "./wallet.db", //db name
    synchronize: false,
    entities: [user, wallet, currency, location, transaction, credential],
});

export default SqliteDataSource;