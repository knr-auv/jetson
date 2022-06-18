import Selector from './Selector.mjs'

export default class InterruptSelector extends Selector{
	constructor({children = [], name = 'InterruptSelector', options = {}} = {}){
		super({
			name,
			children,
			options
		});
	}
	
	load(tick){
		this.runIndex = 0;
	}
	
	tick(tick) {
		let previous = this.runIndex;
		this.load(tick);
		var state = super.tick(tick);
		if (previous != this.runIndex) {
			for (let i = this.runIndex + 1; i < this.children.length; i++)
				this.children[i].abort(tick);
			//this.children[previous].lastState = 'FAILURE';
			if (this.children[previous].lastState == 'RUNNING') {
				this.children[previous].abort(tick);
			}
		}

		return state;
	}
}