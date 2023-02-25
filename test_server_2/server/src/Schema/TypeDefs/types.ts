import { GraphQLObjectType, GraphQLID, GraphQLString, GraphQLFloat, GraphQLList, graphql } from "graphql";

export const UserType = new GraphQLObjectType({
    name: "User",
    fields: () => ({
        id: {type: GraphQLID},
        firstName: {type: GraphQLString},
        lastName: {type: GraphQLString},
        description: {type: GraphQLString},
        wallets: {type: new GraphQLList(GraphQLID)},
        friends: {type: new GraphQLList(GraphQLID)},
    }),
});

export const WalletType = new GraphQLObjectType({
    name: "Wallet",
    fields: () => ({
        id: {type: GraphQLID},
        name: {type: GraphQLString},
        currencyId: {type: GraphQLID},
        transactions: {type: new GraphQLList(GraphQLID)},
        userId: {type: GraphQLID},
        balance: {type: GraphQLFloat},
    }),
});

export const TransactionType = new GraphQLObjectType({
    name: "Transaction",
    fields: () => ({
        id: {type: GraphQLID},
        amount: {type: GraphQLFloat},
        rate: {type: GraphQLFloat},
        payerId: {type: GraphQLID},
        walletId: {type: GraphQLID},
        description: {type: GraphQLString},
        locationId: {type: GraphQLID},
        timestamp: {type: GraphQLString},
    }),
});

export const CurrencyType = new GraphQLObjectType({
    name: "Currency",
    fields: () => ({
        id: {type: GraphQLID},
        abbreviation: {type: GraphQLString},
        symbol: {type: GraphQLString},
        country: {type: GraphQLString},
    }),
});


export const LocationType = new GraphQLObjectType({
    name: "Location",
    fields: () => ({
        id: {type: GraphQLID},
        lat: {type: GraphQLFloat},
        lng: {type: GraphQLFloat},
        name: {type: GraphQLString},
    }),
});