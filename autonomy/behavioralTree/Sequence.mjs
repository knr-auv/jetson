import Composite from './Composite.mjs';

export default class Sequence extends Composite{
	constructor({children = [], name = 'Sequence', options = {}} = {}){
		super({
			name,
			children,
			options
		});
		this.runIndex = 0;
	}
  
	load(tick){
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
			if (state == 'FAILURE'){
				this.runIndex = 0;
				return state;
			}
		}
		return 'SUCCESS';
	}
}