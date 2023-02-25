import express from "express";
import { graphqlHTTP } from "express-graphql";
import { schema } from "./Schema"
import cors from "cors";
import { createConnection } from "typeorm";
import { user } from "./Entities/user";
import { wallet } from "./Entities/wallet";
import { currency } from "./Entities/currency";
import { location } from "./Entities/location";
import { transaction } from "./Entities/transaction";


const main =async () => {

    await createConnection({
        type: "mysql",
        database: "graphQL", //db name
        username: "user", //db user name
        password: "password", //db user password
        // host: "127.0.0.1", //specify host IP, if localhost can delete this
        // port: 1234, //specify mysql port, if default port can delete this
        logging: true,
        synchronize: false,
        entities: [user, wallet, currency, location, transaction],
    })


    const app = express();
    app.use(cors());
    app.use(express.json());
    app.use("/graphql", graphqlHTTP({
        schema,
        graphiql: true
    }))

    app.listen(3001, () => {
        console.log("Server running on port 3001");
    });
};

main().catch((err) => {
    console.log(err);
});