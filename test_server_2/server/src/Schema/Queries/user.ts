import { GraphQLList } from "graphql";
import { UserType } from "../TypeDefs/types";
import { user } from "../../Entities/user";


export const GET_USERS = {
    type: new GraphQLList(UserType),
    resolve() {
        return user.find();
    }
}

export const GET_USER = {
    type: new GraphQLList(UserType),
    resolve(parent: any, args: any) {
        const id = args.id;
        return user.findOne({where: {id: id}});
    }
}