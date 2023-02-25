import { BaseEntity, Column, Entity, PrimaryGeneratedColumn } from "typeorm";

@Entity()
export class user extends BaseEntity {
    
    @PrimaryGeneratedColumn()
    id!: number;
    @Column()
    first_name!: string;
    @Column()
    last_name!: string;
    @Column()
    description!: string;
}