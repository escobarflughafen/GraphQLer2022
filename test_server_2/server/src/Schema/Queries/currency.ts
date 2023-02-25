import { GraphQLList } from "graphql";
import { CurrencyType } from "../TypeDefs/types";
import { currency } from "../../Entities/currency";


export const GET_CURRENCIES = {
    type: new GraphQLList(CurrencyType),
    resolve() {
        return currency.find().then((currencies) => {
            return currencies.map((currency) => ({
                id: currency.id,
                abbreviation: currency.abbreviation,
                symbol: currency.symbol,
                country: currency.country,
            }));
        });;
    }
}

export const GET_CURRENCY = {
    type: CurrencyType,
    resolve(parent: any, args: any) {
        const id = args.id;
        return currency.findOne({where: {id: id}}).then((currency) => {
            return {
                id: currency?.id,
                abbreviation: currency?.abbreviation,
                symbol: currency?.symbol,
                country: currency?.country,
            };
        });
    }
}