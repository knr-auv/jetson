import Node from './Node.mjs';

export default class Action extends Node{
	constructor({name = 'Action', options}={}){
		super({
			type: 'ACTION', //ACTION COMPOSITE DECORATOR CONDITION 
			name,
			options
		});
	}
}