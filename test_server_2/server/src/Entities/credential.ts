import { BaseEntity, Column, Entity, PrimaryGeneratedColumn } from "typeorm";

@Entity()
export class credential extends BaseEntity {
    
    @PrimaryGeneratedColumn()
    id!: number;
    @Column()
    username!: string;
    @Column()
    passwordHash!: string;
}