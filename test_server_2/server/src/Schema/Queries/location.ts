import { GraphQLList } from "graphql";
import { LocationType } from "../TypeDefs/types";
import { location } from "../../Entities/location";


export const GET_LOCATIONS = {
    type: new GraphQLList(LocationType),
    resolve() {
        return location.find();
    }
}

export const GET_LOCATION = {
    type: new GraphQLList(LocationType),
    resolve(parent: any, args: any) {
        const id = args.id;
        return location.findOne({where: {id: id}});
    }
}