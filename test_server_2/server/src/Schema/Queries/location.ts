import { GraphQLList, GraphQLID } from "graphql";
import { LocationType } from "../TypeDefs/types";
import { location } from "../../Entities/location";


export const GET_LOCATIONS = {
    type: new GraphQLList(LocationType),
    resolve() {
        return location.find().then((locations) => {
            return locations.map((location) => ({
                id: location.id,
                lat: location.lat,
                lng: location.lng,
                name: location.name,
            }));
        });;
    }
}

export const GET_LOCATION = {
    type: LocationType,
    args: {
        id: {type: GraphQLID},
    },
    resolve(parent: any, args: any) {
        const id = args.id;
        // should add null detection
        return location.findOne({where: {id: id}}).then((location) => {
            return {
                id: location?.id,
                lat: location?.lat,
                lng: location?.lng,
                name: location?.name,
            };
        });
    }
}