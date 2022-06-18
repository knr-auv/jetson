import Action from './Action.mjs';

export default class Random extends Action{
	constructor({name = 'Random', options}={}){
		super({
			type: 'ACTION',
			name,
			options
		});
	}
	
	tick(tick){
		return Math.random() > .95 ? 'SUCCESS' : 'FAILURE';
	}
}