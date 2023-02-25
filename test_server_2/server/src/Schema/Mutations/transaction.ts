import { GraphQLID, GraphQLString, GraphQLFloat } from "graphql";
import { TransactionType } from "../TypeDefs/types";
import { transaction } from "../../Entities/transaction";

export const CREATE_TRANSACTION = {
    type: TransactionType,
    args: {
        amount: {type: GraphQLFloat},
        rate: {type: GraphQLFloat},
        payerId: {type: GraphQLID},
        walletId: {type: GraphQLID},
        description: {type: GraphQLString},
        locationId: {type: GraphQLID},
    },
    async resolve(parent: any, args: any) {
        const { amount, rate, payerId, walletId, description, locationId } = args;
        return await transaction.insert({ 
            timestamp: Date.now(), 
            amount: amount, 
            rate: rate, 
            payer_id: payerId,
            wallet_id: walletId,
            description: description,
            location_id: locationId,
         });
    },
};

export const UPDATE_TRANSACTION = {
    type: TransactionType,
    args: {
        id: {type: GraphQLID},
        amount: {type: GraphQLFloat},
        rate: {type: GraphQLFloat},
        payerId: {type: GraphQLID},
        walletId: {type: GraphQLID},
        description: {type: GraphQLString},
        locationId: {type: GraphQLID},
    },
    async resolve(parent: any, args: any) {
        const { id, amount, rate, payerId, walletId, description, locationId } = args;
        const target = await transaction.findOne({where: {id: id}});
        if (target != null) {
            return await transaction.update({ id: id }, { 
                amount: amount, 
                rate: rate, 
                payer_id: payerId,
                wallet_id: walletId,
                description: description,
                location_id: locationId,
            });
        } else {
            throw new Error("ID did not exists!");
        }
    },
}

export const DELETE_TRANSACTION = {
    type: TransactionType,
    args: {
        id: {type: GraphQLID},
    },
    async resolve(parent: any, args: any) {
        const id = args.id;
        //await Users.delete(id);
        return await transaction.delete({id: id});
    },
}