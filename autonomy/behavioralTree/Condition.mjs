import Node from './Node.mjs';

export default class Condition extends Node{
	constructor({name = 'Condition', condition, options}={}){
		super({
			type: 'CONDITION', 
			name,
			options
		});
		this.condition = condition;
	}
	
	tick(tick){
		return this.condition(tick)? 'SUCCESS' : 'FAILURE';
	}
}