function consolelog(...x){
	for(let i = 0; i < x.length; i++){
		process.stdout.write(x[i]);
		process.stdout.write(" ");
	}
	process.stdout.write("                     \n");
}
export default class Node{
	static id = 0;
	constructor({type, name, options} = {}){
		this.id = Node.id++;
		this.type = type || '';
		this.name = name || '';
		this.options = options || {};
		this.lastState = 'UNKNOWN';
	}
	
	run(tick){
		tick.loadNode(this);
		if(!tick.blackboard.get('isLoaded', this.id)){
			tick.blackboard.set('isLoaded', true, this.id);
			this.load(tick);
		}
		
		this.lastState = this.tick(tick);
		
		if(this.lastState !== 'RUNNING'){
			tick.leaveNode(this);
			tick.blackboard.set('isLoaded', false, this.id);
			this.unload(tick);
		}
		return this.lastState;
	}
	
	print(indent, last = false, isRoot = true, blackboard){
		let str = indent;
		if (!isRoot){
			if (last) {
				str += ("╚─");
				indent += "  ";
			} else {
				str+=("╠─");
				indent += "║ ";
			}
		}
		let color = '';
		if(this.lastState === 'UNKNOWN') color = "\x1b[2m" + "\x1b[47m";
		if(this.lastState === 'SUCCESS') color = "\x1b[42m";
		if(this.lastState === 'RUNNING') color = "\x1b[43m";
		if(this.lastState === 'FAILURE') color = "\x1b[41m";
		if(this.type == 'ACTION' || this.type == 'COMPOSITE') consolelog(str + "\x1b[30m" + color + '[' + this.name + ']' + "\x1b[0m", blackboard.get('isLoaded', this.id)?'LOADED':'');
		if(this.type == 'CONDITION') consolelog(str + "\x1b[30m" + color + '(' + this.name + ')' + "\x1b[0m", blackboard.get('isLoaded', this.id)?'LOADED':'');
		if(this.type == 'DECORATOR') consolelog(str + "\x1b[30m" + color + '<' + this.name + '>' + "\x1b[0m", blackboard.get('isLoaded', this.id)?'LOADED':'');
		
		if(this.type == 'COMPOSITE'){
			for (let i = 0; i < this.children.length; i++)
			this.children[i].print(indent, i == this.children.length - 1, false, blackboard);
		}else if(this.type == 'DECORATOR'){
			this.child.print(indent, true, false, blackboard);
		}else return;
		
		if(isRoot)consolelog('');
	}
	
	resetState(blackboard){
		this.lastState = 'UNKNOWN';
		if(this.type !== 'COMPOSITE') return;
		for (let i = 0; i < this.children.length; i++)
			this.children[i].resetState(blackboard);
	}
	
	load(tick){}
	tick(tick){}
	unload(tick){}
	abort(tick){
	
		this.onAbort();
		tick.blackboard.set('isLoaded', false, this.id);
		this.lastState = 'UNKNOWN';
		this.unload(tick);
		if(this.children){
			for(let i = 0; i < this.children.length; i++)
				this.children[i].abort(tick);
		}
		if(this.child){
			this.child.abort(tick);
		}
	}
	
	onAbort(){}
}