import Composite from './Composite.mjs';

export default class Selector extends Composite{
	constructor({children = [], name = 'Selector', options = {}} = {}){
		super({
			name,
			children,
			options
		});
		this.runIndex = 0;
	}
	
	load(tick){
		console.log(this.name);
		this.resetState(tick.blackboard);
		this.runIndex = 0;
	}
	
	tick(tick) {
		for (let i = this.runIndex; i < this.children.length; i++) {
			let state = this.children[i].run(tick);
			if(state == 'RUNNING'){
				this.runIndex = i;
				return state;
			}
			if (state == 'SUCCESS'){
				this.runIndex = 0;
				return state;
			}
		}
		return 'FAILURE';
	}
}