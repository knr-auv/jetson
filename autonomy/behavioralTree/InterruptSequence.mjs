import Sequence from './Sequence.mjs'

export default class InterruptSequence extends Sequence{
	constructor({children = [], name = 'InterruptSequence', options = {}} = {}){
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
				
			if (this.children[previous].lastState == 'RUNNING')
				this.children[previous].abort(tick);
		}
		return state;
	}
}