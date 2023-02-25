import { BaseEntity, Column, Entity, PrimaryGeneratedColumn } from "typeorm";

@Entity()
export class wallet extends BaseEntity {
    
    @PrimaryGeneratedColumn()
    id!: number;
    @Column()
    name!: string;
    @Column()
    currency_id!: number;
    @Column()
    owner_id!: number;
}