import { BaseEntity, Column, Entity, PrimaryGeneratedColumn } from "typeorm";

@Entity()
export class currency extends BaseEntity {
    
    @PrimaryGeneratedColumn()
    id!: number;
    @Column()
    country!: string;
    @Column()
    abbreviation!: string;
    @Column()
    symbol!: string;
}