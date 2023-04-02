import express from "express";
import { graphqlHTTP } from "express-graphql";
import { schema } from "./Schema"
import cors from "cors";
import SqliteDataSource from "./sqlite";
import { user } from "./Entities/user";
import { wallet } from "./Entities/wallet";
import { currency } from "./Entities/currency";
import { location } from "./Entities/location";
import { transaction } from "./Entities/transaction";
import { credential } from "./Entities/credential";
import { authMiddleware, fetchUserByUsername, generateBasicToken, generateJsonWebToken } from "./auth";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import fs from "fs";

const JWT_SECRET = fs.readFileSync("./.jwtsecret", "ascii");

const main = async () => {

    SqliteDataSource.initialize().then(
        async () => {
            await credential.insert({
                username: "testuser",
                passwordHash: await bcrypt.hash("123456", 10)
            });
            console.log("Data Source has been established")
        }
    ).catch(
        (err) => console.error("Error during Data Source initialization", err)
    );

    const app = express();
    app.use(cors());
    app.use(express.json());


    app.post("/login", async (req, res) => {
        const {username, password} = req.body;
         
        const user = await fetchUserByUsername(username);
        if (user) {
            const result = await bcrypt.compare(password, user?.passwordHash);
            if (result) {
                return res.status(200).json({
                    token: generateJsonWebToken(user.id)
                })
            } else {
                return res.status(401).json({message: "Invalid token."});
            }
        } else {
            return res.status(404).json({message: "User not found."});
        }
    });
    app.use("/basiclogin", async (req, res) => {
        const {username, password} = req.body;
         
        const user = await fetchUserByUsername(username);
        if (user) {
            const result = await bcrypt.compare(password, user?.passwordHash);
            if (result) {
                return res.status(200).json({
                    token: generateBasicToken(user)
                })
            } else {
                return res.status(401).json({message: "Invalid token."});
            }
        } else {
            return res.status(404).json({message: "User not found."});
        }
    });
    app.use("/graphql", authMiddleware);
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