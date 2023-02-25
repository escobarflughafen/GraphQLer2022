import { BaseEntity, Column, Entity, PrimaryGeneratedColumn } from "typeorm";

@Entity()
export class transaction extends BaseEntity {
    
    @PrimaryGeneratedColumn()
    id!: number;
    @Column()
    timestamp!: number;
    @Column()
    payer_id!: number;
    @Column()
    wallet_id!: number;
    @Column()
    shared_with!: string;
    @Column()
    currency_id!: number;
    @Column()
    rate!: number;
    @Column()
    amount!: number;
    @Column()
    location_id!: number;
    @Column()
    description!: string;
}