import { GraphQLList } from "graphql";
import { WalletType } from "../TypeDefs/types";
import { wallet } from "../../Entities/wallet";


export const GET_WALLETS = {
    type: new GraphQLList(WalletType),
    resolve() {
        return wallet.find();
    }
}

export const GET_WALLET = {
    type: new GraphQLList(WalletType),
    resolve(parent: any, args: any) {
        const id = args.id;
        return wallet.findOne({where: {id: id}});
    }
}