import jwt from "jsonwebtoken";
import bcrypt from "bcrypt";
import fs from "fs";
import { credential } from "./Entities/credential";
import sqlite3 from "sqlite3";

const JWT_SECRET = fs.readFileSync("./.jwtsecret", "ascii");


export async function fetchUserById(id: any) {
    const user = await credential.findOne(id);

    return user;
}

export async function fetchUserByUsername(username: string) {
    /*
    const db = new sqlite3.Database("./wallet.db");
    const passwordHash = await bcrypt.

    const user = db.get(`SELECT * FROM escredential WHERE username={} and pass`, [username], (error, row) => {
        
    });
    

    db.close();
    */

    const user = await credential.findOneBy({username: username});
    
    return user;
}

export function generateJsonWebToken(id: any) {
    const payload = {
        id: id
    };
    return jwt.sign(payload, JWT_SECRET);
}

export function generateBasicToken(user: any) {
    const token = Buffer.from(`${user.username}:${user.password}`).toString("base64");
    return token
}


export async function authMiddleware(req: any, res: any, next: any) {
    const auth = req.headers.authorization;

    if (!auth) {
        return res.status(401).json({
            message: "No authorization token provided."
        })
    }

    if (auth.startsWith("Basic ")) {
        const base64Credentials = auth.split(" ")[1];
        const credentials = Buffer.from(base64Credentials, "base64").toString("ascii");
        
        const [username, password] = credentials.split(":");
        const user = await fetchUserByUsername(username);
        if (user) {
            const result = await bcrypt.compare(password, user?.passwordHash);
            if (result) {
                req.user = user;
            } else {
                return res.status(401).json({message: "Invalid token."});
            }
        } else {
            return res.status(404).json({message: "User not found."});
        }
    } else if (auth.startsWith("Bearer ")) {
        const jsonWebToken = auth.split(" ")[1];
        try{
            const credentials = jwt.verify(jsonWebToken, JWT_SECRET) as {id: number};
            const user = await fetchUserById(credentials.id);
            req.user = user;
        } catch (error) {
            return res.status(401).json({message: 'Malformed token.'})
        }
    } else {
        return res.status(401).json({
            message: "Unsupported authorization method."
        })
    }

    next();
}