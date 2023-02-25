import { GraphQLID, GraphQLString, GraphQLFloat } from "graphql";
import { LocationType } from "../TypeDefs/types";
import { location } from "../../Entities/location";



export const CREATE_LOCATION = {
    type: LocationType,
    args: {
        lat: {type: GraphQLFloat},
        lng: {type: GraphQLFloat},
        name: {type: GraphQLString},
    },
    async resolve(parent: any, args: any) {
        const { lat, lng, name } = args;
        return await location.insert({ 
            name: name, 
            lat: lat, 
            lng: lng, 
        });
    },
};

export const UPDATE_LOCATION = {
    type: LocationType,
    args: {
        id: {type: GraphQLID},
        lat: {type: GraphQLFloat},
        lng: {type: GraphQLFloat},
        name: {type: GraphQLString},
    },
    async resolve(parent: any, args: any) {
        const { id, lat, lng, name } = args;
        const target = await location.findOne({where: {id: id}});
        if (target != null) {
            return await location.update({id: id}, { 
                lat: lat, 
                lng: lng, 
                name: name, 
            });
        } else {
            throw new Error("ID did not exists!");
        }
    },
}

export const DELETE_LOCATION = {
    type: LocationType,
    args: {
        id: {type: GraphQLID},
    },
    async resolve(parent: any, args: any) {
        const id = args.id;
        //await Users.delete(id);
        return await location.delete({id: id});
    },
}