import Action from './Action.mjs'
export default class Wait extends Action{
	constructor({name = 'Wait <milliseconds>ms', milliseconds = 0} = {}) {
		super({
			name: name.replace("<milliseconds>", milliseconds),
			options: {milliseconds: 0}
		});

		this.endTime = milliseconds;
	}
	
	load(tick) {
		let startTime = (new Date()).getTime();
		tick.blackboard.set('startTime', startTime, this.id);
	}
	
	tick(tick) {
		let currTime = (new Date()).getTime();
		let startTime = tick.blackboard.get('startTime', this.id);

		if (currTime - startTime > this.endTime)
			return 'SUCCESS';
		return 'RUNNING';
	}
}