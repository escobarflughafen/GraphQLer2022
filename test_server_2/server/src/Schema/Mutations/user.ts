import { GraphQLID, GraphQLString } from "graphql";
import { UserType } from "../TypeDefs/types";
import { user } from "../../Entities/user";



export const CREATE_USER = {
    type: UserType,
    args: {
        firstName: {type: GraphQLString},
        lastName: {type: GraphQLString},
        description: {type: GraphQLString},
    },
    async resolve(parent: any, args: any) {
        const { firstName, lastName, description } = args;
        return await user.insert({ 
            first_name: firstName, 
            last_name: lastName, 
            description: description 
        });
    },
};

export const UPDATE_USER = {
    type: UserType,
    args: {
        id: {type: GraphQLID},
        firstName: {type: GraphQLString},
        lastName: {type: GraphQLString},
        description: {type: GraphQLString},
    },
    async resolve(parent: any, args: any) {
        const { id, firstName, lastName, description } = args;
        const target = await user.findOne({where: {id: id}});
        if (target != null) {
            return await user.update({id: id}, { 
                first_name: firstName, 
                last_name: lastName, 
                description: description 
            });
        } else {
            throw new Error("ID did not exists!");
        }
    },
}

export const DELETE_USER = {
    type: UserType,
    args: {
        id: {type: GraphQLID},
    },
    async resolve(parent: any, args: any) {
        const id = args.id;
        //await Users.delete(id);
        return await user.delete({id: id});
    },
}