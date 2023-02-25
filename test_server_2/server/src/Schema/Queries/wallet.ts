import { GraphQLList, GraphQLID } from "graphql";
import { WalletType } from "../TypeDefs/types";
import { wallet } from "../../Entities/wallet";


export const GET_WALLETS = {
    type: new GraphQLList(WalletType),
    resolve() {
        return wallet.find().then((wallets) => {
            return wallets.map((wallet) => ({
                id: wallet.id,
                name: wallet.name,
                currencyId: wallet.currency_id,
                transactions: null, //should be changed to list of IDs by finding related transactions
                userId: wallet.owner_id,
                balance: 0.0, //should calculate all transactions and return result here
            }));
        });;
    }
}

export const GET_WALLET = {
    type: WalletType,
    args: {
        id: {type: GraphQLID},
    },
    resolve(parent: any, args: any) {
        const id = args.id;
        // should add null detection
        return wallet.findOne({where: {id: id}}).then((wallet) => {
            return {
                id: wallet?.id,
                name: wallet?.name,
                currencyId: wallet?.currency_id,
                transactions: null, //should be changed to list of IDs by finding related transactions
                userId: wallet?.owner_id,
                balance: 0.0, //should calculate all transactions and return result here
            };
        });
    }
}