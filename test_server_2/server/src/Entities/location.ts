import { BaseEntity, Column, Entity, PrimaryColumn } from "typeorm";

@Entity()
export class location extends BaseEntity {
    
    @PrimaryColumn()
    id!: string;
    @Column()
    name!: string;
    @Column()
    lat!: number;
    @Column()
    lng!: number;
}