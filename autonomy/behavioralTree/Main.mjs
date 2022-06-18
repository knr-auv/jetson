import Node from './Node.mjs'
import Composite from './Composite.mjs'
import Selector from './Selector.mjs'
import InterruptSelector from './InterruptSelector.mjs'
import Sequence from './Sequence.mjs'
//const Decorator = require('./Decorator.js');
import Action from './Action.mjs'
import Wait from './Wait.mjs'
import Random from './Random.mjs'
import Blackboard from './Blackboard.mjs'
import Tick from './Tick.mjs'


class TestAction extends Action{
	constructor(name, state = 'SUCCESS'){
		super({name:'ActionNode ' + name});
		this.state = state;
	}
	
	tick(tick){
		return this.state;
	}
}

let b = new Blackboard();

let root =	
new InterruptSelector({
	children:[
		new Sequence({
			children:[
				new Random(),
				new Wait({milliseconds:1000}),
				new TestAction('INTERRUPTED')
			]
		}),
		new Sequence({
			children:[
				new Sequence({
					children:[
						new TestAction('A'),
						new Wait({milliseconds:1000}),
						new TestAction('B'),
						new Sequence({
							children:[
								new TestAction('0'),
								new TestAction('1'),
								new TestAction('1'),
							]
						})
					]
				}),
				new Sequence({
					children:[
						new TestAction('C'),
						new Wait({milliseconds:1000}),
						new TestAction('D','SUCCESS'),
						new Wait({milliseconds:1000}),
						new TestAction('E')
					]
				})
			]
		})
	]
});


root.resetState(b); //DRAW TREE

let ll = setInterval(()=>{

	let t = new Tick({tree: {}, blackboard: b});
	let state = root.run(t);	
	
	console.clear(); //console.log("\x1b[0;0H");
	console.log(state);	
	root.print('#      ', false, true, b); //DRAW TREE
	
	console.log(t.loadedNodesNum, t.loadedNodes.map(n=>n.name));
}, 200);