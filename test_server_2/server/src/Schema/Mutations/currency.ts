import { GraphQLID, GraphQLString, GraphQLFloat } from "graphql";
import { CurrencyType } from "../TypeDefs/types";
import { currency } from "../../Entities/currency";



export const CREATE_CURRENCY = {
    type: CurrencyType,
    args: {
        abbreviation: {type: GraphQLString},
        symbol: {type: GraphQLString},
        country: {type: GraphQLString},
    },
    async resolve(parent: any, args: any) {
        const { abbreviation, symbol, country } = args;
        return await currency.insert({ 
            abbreviation: abbreviation, 
            symbol: symbol, 
            country: country, 
        });
    },
};

export const UPDATE_CURRENCY = {
    type: CurrencyType,
    args: {
        id: {type: GraphQLID},
        abbreviation: {type: GraphQLString},
        symbol: {type: GraphQLString},
        country: {type: GraphQLString},
    },
    async resolve(parent: any, args: any) {
        const { id, abbreviation, symbol, country } = args;
        const target = await currency.findOne({where: {id: id}});
        if (target != null) {
            return await currency.update({id: id}, { 
                abbreviation: abbreviation, 
                symbol: symbol, 
                country: country, 
            });
        } else {
            throw new Error("ID did not exists!");
        }
    },
}

export const DELETE_CURRENCY = {
    type: CurrencyType,
    args: {
        id: {type: GraphQLID},
    },
    async resolve(parent: any, args: any) {
        const id = args.id;
        //await Users.delete(id);
        return await currency.delete({id: id});
    },
}