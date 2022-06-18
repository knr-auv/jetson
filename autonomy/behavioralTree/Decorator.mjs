import Node from './Node.mjs';

export default class Decorator extends Node{
	constructor({child, name = 'Decorator', options}={}){
		super({
			type: 'DECORATOR', 
			name,
			options
		});
		this.child = child;//TODO getchildren
	}
}