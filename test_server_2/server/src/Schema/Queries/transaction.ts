import { GraphQLList } from "graphql";
import { TransactionType } from "../TypeDefs/types";
import { transaction } from "../../Entities/transaction";


export const GET_TRANSACTIONS = {
    type: new GraphQLList(TransactionType),
    resolve() {
        return transaction.find().then((transactions) => {
            return transactions.map((transaction) => ({
                id: transaction.id,
                amount: transaction.amount,
                rate: transaction.rate,
                payerId: transaction.payer_id,
                walletId: transaction.wallet_id,
                description: transaction.description,
                locationId: transaction.location_id,
                timestamp: transaction.timestamp,
            }));
        });;
    }
}

export const GET_TRANSACTION = {
    type: TransactionType,
    resolve(parent: any, args: any) {
        const id = args.id;
        return transaction.findOne({where: {id: id}}).then((transaction) => {
            return {
                id: transaction?.id,
                amount: transaction?.amount,
                rate: transaction?.rate,
                payerId: transaction?.payer_id,
                walletId: transaction?.wallet_id,
                description: transaction?.description,
                locationId: transaction?.location_id,
                timestamp: transaction?.timestamp,
            };
        });
    }
}