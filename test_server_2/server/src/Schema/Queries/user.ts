import { GraphQLList, GraphQLID } from "graphql";
import { UserType } from "../TypeDefs/types";
import { user } from "../../Entities/user";


export const GET_USERS = {
    type: new GraphQLList(UserType),
    resolve() {
        return user.find().then((users) => {
            return users.map((user) => ({
                id: user.id,
                firstName: user.first_name,
                lastName: user.last_name,
                description: user.description,
            }));
        });
    },
}

export const GET_USER = {
    type: UserType,
    args: {
        id: {type: GraphQLID},
    },
    resolve(parent: any, args: any) {
        const id = args.id;
        // should add null detection
        return user.findOne({where: {id: id}}).then((user) => {
            return {
                id: user?.id,
                firstName: user?.first_name,
                lastName: user?.last_name,
                description: user?.description,
            };
        });
    }
}