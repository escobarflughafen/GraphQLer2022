import { GraphQLObjectType, GraphQLSchema } from "graphql";
import { GET_USERS, GET_USER } from "./Queries/user";
import { GET_TRANSACTIONS, GET_TRANSACTION } from "./Queries/transaction";
import { GET_LOCATION, GET_LOCATIONS } from "./Queries/location";
import { GET_CURRENCIES, GET_CURRENCY } from "./Queries/currency";
import { GET_WALLETS, GET_WALLET } from "./Queries/wallet";
import { CREATE_USER, UPDATE_USER, DELETE_USER } from "./Mutations/user";
import { CREATE_WALLET, DELETE_WALLET, UPDATE_WALLET } from "./Mutations/wallet";
import { CREATE_TRANSACTION, DELETE_TRANSACTION, UPDATE_TRANSACTION } from "./Mutations/transaction";
import { CREATE_LOCATION, DELETE_LOCATION, UPDATE_LOCATION } from "./Mutations/location";
import { CREATE_CURRENCY, DELETE_CURRENCY, UPDATE_CURRENCY } from "./Mutations/currency";

const RootQuery = new GraphQLObjectType({
    name: "RootQuery",
    fields: {
        getUsers: GET_USERS,
        getUser: GET_USER,
        getTransactions: GET_TRANSACTIONS,
        getTransaction: GET_TRANSACTION,
        getLocations: GET_LOCATIONS,
        getLocation: GET_LOCATION,
        getCurrencies: GET_CURRENCIES,
        getCurrency: GET_CURRENCY,
        getWallets: GET_WALLETS,
        getWallet: GET_WALLET,
    },
});

const Mutation = new GraphQLObjectType({
    name: "Mutation",
    fields: {
        createUser: CREATE_USER,
        updateUser: UPDATE_USER,
        deleteUser: DELETE_USER,
        createTransaction: CREATE_TRANSACTION,
        updateTransaction: UPDATE_TRANSACTION,
        deleteTransaction: DELETE_TRANSACTION,
        createLocation: CREATE_LOCATION,
        updateLocation: UPDATE_LOCATION,
        deleteLocation: DELETE_LOCATION,
        createCurrency: CREATE_CURRENCY,
        updateCurrency: UPDATE_CURRENCY,
        deleteCurrency: DELETE_CURRENCY,
        createWallet: CREATE_WALLET,
        updateWallet: UPDATE_WALLET,
        deleteWallet: DELETE_WALLET,
    },
});

export const schema = new GraphQLSchema({
    query: RootQuery,
    mutation: Mutation,
});