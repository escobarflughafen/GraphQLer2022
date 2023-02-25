import { GraphQLList } from "graphql";
import { CurrencyType } from "../TypeDefs/types";
import { currency } from "../../Entities/currency";


export const GET_CURRENCIES = {
    type: new GraphQLList(CurrencyType),
    resolve() {
        return currency.find();
    }
}

export const GET_CURRENCY = {
    type: new GraphQLList(CurrencyType),
    resolve(parent: any, args: any) {
        const id = args.id;
        return currency.findOne({where: {id: id}});
    }
}