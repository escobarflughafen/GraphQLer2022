import { GraphQLID, GraphQLString } from "graphql";
import { WalletType } from "../TypeDefs/types";
import { wallet } from "../../Entities/wallet";

export const CREATE_WALLET = {
    type: WalletType,
    args: {
        name: {type: GraphQLString},
        currencyId: {type: GraphQLID},
        userId: {type: GraphQLID},
    },
    async resolve(parent: any, args: any) {
        const { name, currencyId, userId } = args;
        return await wallet.insert({ 
            name: name, 
            currency_id: currencyId, 
            owner_id: userId 
        });
    },
};

export const UPDATE_WALLET = {
    type: WalletType,
    args: {
        id: {type: GraphQLID},
        name: {type: GraphQLString},
    },
    async resolve(parent: any, args: any) {
        const { id, name } = args;
        const target = await wallet.findOne({where: {id: id}});
        if (target != null) {
            return await wallet.update({id: id}, { 
                name: name 
            });
        } else {
            throw new Error("ID did not exists!");
        }
    },
}

export const DELETE_WALLET = {
    type: WalletType,
    args: {
        id: {type: GraphQLID},
    },
    async resolve(parent: any, args: any) {
        const id = args.id;
        //await Users.delete(id);
        return await wallet.delete({id: id});
    },
}