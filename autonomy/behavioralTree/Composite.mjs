import Node from './Node.mjs';

export default class Composite extends Node{
	constructor({children, name = 'Composite', options}={}){
		super({
			type: 'COMPOSITE', //ACTION COMPOSITE DECORATOR CONDITION 
			name,
			options
		});
		this.children = children.slice(0);
	}
}