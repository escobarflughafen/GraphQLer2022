import { GraphQLList } from "graphql";
import { TransactionType } from "../TypeDefs/types";
import { transaction } from "../../Entities/transaction";


export const GET_TRANSACTIONS = {
    type: new GraphQLList(TransactionType),
    resolve() {
        return transaction.find();
    }
}

export const GET_TRANSACTION = {
    type: new GraphQLList(TransactionType),
    resolve(parent: any, args: any) {
        const id = args.id;
        return transaction.findOne({where: {id: id}});
    }
}