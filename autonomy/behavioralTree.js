'use strict';
function consolelog(...x){
	for(let i = 0; i < x.length; i++){
		process.stdout.write(x[i]);
		process.stdout.write(" ");
	}
	process.stdout.write("                     \n");
}
console.clear();
let gokon;
(async ()=>{
const {OkonClient, PacketType, PacketFlag} = require('./okonClient');
const {Wait, Blackboard, Tick, Action, InterruptSelector,InterruptSequence, Decorator, Sequence, Condition, Selector} = await import('./behavioralTree/BT.mjs');
const fs = require('fs');

let okonClient = new OkonClient('127.0.0.1', '44210', {SHOW_PACKET_TIME:false,TOTAL_SYNC:50, GET_CPS:500});
let {okon, simulation} = okonClient;
gokon = okon;
okonClient.on('connected', ()=>{
	console.log('connected');
	okon.setDepth(1.5);
	setInterval(()=>exe(),100);
});

simulation.on('hitNGZ', ()=>{
	b.set('reset', true);
});

simulation.on('reset', ()=>{
	b.set('reset', true);
    
});

simulation.on('hitFZ', ()=>{
	b.set('reset', true);
});

okonClient.connect();	

class DummyAction extends Action{
	constructor(name = 'DummyAction always <state>', state = 'SUCCESS'){
		super({name: name.replace('<state>', state)});
		this.state = state;
	}
	
	tick(tick){
		return this.state;
	}
}

class Succeed extends Condition{
	constructor(name = 'Succeed'){
		super({
			type: 'CONDITION', 
			name,
			condition: ()=>true
		});
	}
}

class Fail extends Condition{
	constructor(name = 'Fail'){
		super({
			type: 'CONDITION', 
			name,
			condition: ()=>false
		});
	}
}


class Rotate extends Action{
	constructor({name = 'Rotate <delta>', delta = 0} = {}){
		super({name: name.replace("<delta>", delta)});
		this.delta = delta;
	}
	
	load(tick){
		super.load(tick);
		tick.blackboard.get('okon').setRot(null, this.delta, null, true);
	}
	
	tick(tick){
		if(tick.blackboard.get('okon').reachedTargetRotation(5))return 'SUCCESS';
		else return 'RUNNING';
	}
}

class ReachTargetRotation extends Action{
	constructor({name = 'ReachTargetRotation d<delta>', delta = 2} = {}){
		super({name: name.replace("<delta>", delta)});
		this.delta = delta;
	}
	
	tick(tick){
		if(tick.blackboard.get('okon').reachedTargetRotation(this.delta))return 'SUCCESS';
		else return 'RUNNING';
	}
}

class ReachTargetDepth extends Action{
	constructor({name = 'ReachTargetDepth d<delta>', delta = .1} = {}){
		super({name: name.replace("<delta>", delta)});
		this.delta = delta;
	}
	
	tick(tick){
		if(tick.blackboard.get('okon').reachedTargetDepth(this.delta))return 'SUCCESS';
		else return 'RUNNING';
	}
}

class GoForward extends Action{
	constructor({name = 'GoForward <fill>', fill = 0} = {}){
		super({name: name.replace("<fill>", fill)});
		this.fill = fill;
	}
	
	tick(tick){
		tick.blackboard.get('okon').setStableVel(null, null, this.fill, false);
		return 'SUCCESS';
	}
}

class Runner extends Action{
	constructor({name = 'Runner', func} = {}){
		super({name});
		this.func = func;
	}
	
	tick(tick){
		this.func(tick);
		return 'SUCCESS';
	}
}

class BooleanRunner extends Action{
	constructor({name = 'Runner', func} = {}){
		super({name});
		this.func = func;
	}
	
	tick(tick){
		return this.func(tick) ? 'SUCCESS' : 'FAILURE';
	}
}

class DunamicRotate extends Action{
	constructor({name = 'Rotate <variable>', variable = ""} = {}){
		super({name: name.replace("<variable>", variable)});
        this.variable = variable;
	}
	
	load(tick){
		super.load(tick);
		tick.blackboard.get('okon').setRot(null, tick.blackboard.get(this.variable), null, true);
	}
	
	tick(tick){
		if(tick.blackboard.get('okon').reachedTargetRotation(5))return 'SUCCESS';
		else return 'RUNNING';
	}
}


class RepeatUntilSuccess extends Decorator {
	constructor({child, name = 'RepeatUntilSuccess'}={}){
		super({
			type: 'DECORATOR', 
			name,
			child
		});
	}
	
	tick(tick){
		let state = this.child.run(tick);
		if(state === 'SUCCESS')return state;
		return 'RUNNING';
	}
}

class Invert extends Decorator {
	constructor({child, name = 'Invert'}={}){
		super({
			type: 'DECORATOR', 
			name,
			child
		});
	}
	
	tick(tick){
		let state = this.child.run(tick);
		if(state === 'SUCCESS')return 'FAILURE';
		if(state === 'FAILURE')return 'SUCCESS';
		return 'RUNNING';
	}
}




let b = new Blackboard();
b.set('okon', okon);
b.set('simulation', simulation);

let root = 
new InterruptSelector({
	children:[
		new Sequence({children:[
			new Condition({name: 'Reached gate', condition: (tick)=>{
				let sim = b.get('simulation');
				for(let ch of sim.checkpoints){
					if(ch.id == 'Gate' && ch.reached)return true;
				}
				return false;
			}}),
			new Runner({ name: 'Reset sim', func: (tick)=>{
				b.get('simulation').reset();
			}}),
			new Wait({milliseconds:1000})
		]}),
		new Sequence({children:[
			new Condition({name: 'Simulation was resetted', condition: (tick)=>{
				return b.get('reset');
			}}),
			new Runner({ name: 'Disarm Motors', func: (tick)=>{
				b.get('okon').disarmMotors();
			}}),
			new Runner({ name: 'Reset reset flag', func: (tick)=>{
				b.set('reset', false);
			}}),
			new Runner({ name: 'Reset knownGateNear flag', func: (tick)=>{
				tick.blackboard.get('knownGateNear', false);
			}}),
			new GoForward({name:'Stop', fill:0}),
			new Runner({ name: 'Set Yaw', func: (tick)=>{
				okon.setRot(null, okon.sens.imu.rot.y, null);
			}}),
			new Runner({ name: 'Set Depth', func: (tick)=>{
				b.get('okon').setDepth(1.5);
			}}),
			new Runner({ name: 'Arm Motors', func: (tick)=>{
				b.get('okon').armMotors();
			}}),
			new ReachTargetRotation({delta:5}),
			new ReachTargetDepth({delta:.1}),
			new Wait({milliseconds:1000})
		]}),
		new Fail('Red Flare in the way'),
		new InterruptSequence({children: [
				new GoForward({fill:0}),
				new Selector({name:'Gate Fully visible',children: [
						new Condition({ name: 'Gate Fully Visible', condition: (tick)=>{
								let d = tick.blackboard.get('okon').sens.detection;
								for(let el of d){
									if(el.className == 'gate' && el.visibleInFrame){
										if(el.min.x > 0.01 && el.max.x < 0.99)
										return true;
									}
								}
								return false;
							}
						}),
						new Sequence({children: [
								new Wait({milliseconds:500}),
								new Rotate({delta:20}),
								new Condition({ name: 'Gate Visible', condition: (tick)=>{
										let d = tick.blackboard.get('okon').sens.detection;
										for(let el of d){
											if(el.className == 'gate' && el.visibleInFrame){
												return true;
											}
										}
										return false;
								}})
						]})
				]}),
				new Selector({name:'Gate ratio 0K',children: [
					new Succeed(),
					new Condition({ name: 'Gate ratio 0K', condition: (tick)=>{
								let d = tick.blackboard.get('okon').sens.detection;
								for(let el of d){
									if(el.className == 'gate' && el.visibleInFrame){
										if((el.max.x-el.min.x)/(el.max.y-el.min.y) > .8)
										return true;
									}
								}
								return false;
							}
					}),
					new Sequence({children: [
						new Succeed('Known Gate Near'),
						new Condition({ name: 'knownGateNear', condition: (tick)=>{
								return (tick.blackboard.get('knownGateNear') === true);
							}
						}),
						new Sequence({name:'»Check Near',children: [
								new Fail('Near Left'),
								new Rotate({delta:-90}),
								new GoForward({fill:.5}),
								new Wait({milliseconds:1000}),
								new GoForward({name:'Stop', fill:0}),
								new Rotate({delta:90})
						]}),
						new Selector({children: [
							new Sequence({name:'»Near Left',children: [
								new Fail('Near Left'),
								new Rotate({delta:-90}),
								new GoForward({fill:.5}),
								new Wait({milliseconds:1000}),
								new GoForward({name:'Stop', fill:0}),
								new Rotate({delta:90})
							]}),
							new Sequence({name:'»Near Right',	children: [
								new Succeed('Near Right'),
								new Rotate({delta:-90}),
								new GoForward({fill:.5}),
								new Wait({milliseconds:1000}),
								new GoForward({name:'Stop', fill:0}),
								new Rotate({delta:90})
							]})
						]})
					]})
				]}),
				new Selector({name:'?Gate in the mid',children: [
					new Condition({name: 'Gate in the mid', condition: (tick)=>{
						let d = tick.blackboard.get('okon').sens.detection;
						for(let el of d){
							if(el.className == 'gate' && el.visibleInFrame){
								let gateMid = (el.min.x + el.max.x)/2;
								if(Math.abs(0.5 - gateMid) < 0.05)
								return true;
							}
						}
						return false;
					}}),
					new Sequence({children: [
						new Runner({ name: 'Save gate ratio', func: (tick)=>{
							let d = tick.blackboard.get('okon').sens.detection;
							for(let el of d){
								if(el.className == 'gate' && el.visibleInFrame){
									let gateMid = (el.min.x + el.max.x)/2;
									tick.blackboard.set('gateToTheRight', gateMid - 0.5 > 0)
									return;
								}
							}	
						}}),	
						new Wait({milliseconds:100}),
						new Selector({children: [
							new Sequence({children: [
								new Condition({name: 'gate to the right', condition: (tick)=>{
									return tick.blackboard.get('gateToTheRight');
								}}),
								new Rotate({delta:4})
							]}),
							new Sequence({children: [
								new Condition({name: 'gate to the left', condition: (tick)=>{
									return !tick.blackboard.get('gateToTheRight');
								}}),
								new Rotate({delta:-4})
							]}),
						]}),
						new Condition({name: 'Gate in the mid', condition: (tick)=>{
							let d = tick.blackboard.get('okon').sens.detection;
							for(let el of d){
								if(el.className == 'gate' && el.visibleInFrame){
									let gateMid = (el.min.x + el.max.x)/2;
									if(Math.abs(0.5 - gateMid) < 0.05)
									return true;
								}
							}
							return false;
						}})
					]}),
					new Wait({milliseconds:100})
				]}),
				new GoForward({fill:.5}),
				//new DummyAction('','RUNNING')
			]
		})
	]
});


root = new Selector({children:[
    new Sequence({children:[
        new BooleanRunner({name: "isBB failed to find", func: (t)=>t.blackboard.get('failed-to-find')===true}),
       // new Runner({name: "disable motors", func: (t)=>t.blackboard.get('okon').disarmMotors()}),
        new Succeed()
    ]}),
    new Sequence({name: "move from wall", children:[
        new BooleanRunner({name: "isBB not moved", func: (t)=>t.blackboard.get('moved')!==true}),
        new Runner({name: "setBB moved", func: (t)=>t.blackboard.set('moved', true)}),
        new Runner({name: "set depth to current", func: (t)=>{t.blackboard.get('okon').setDepth(b.get('okon').sens.baro/1000/9.81)}}),
        new Runner({name: "enable motors", func: (t)=>t.blackboard.get('okon').armMotors()}),
        new Runner({name: "move forward", func: (t)=>{t.blackboard.get('okon').setStableVel(null, null, .5, false);}}),
        new Runner({name: "set depth to current", func: (t)=>{t.blackboard.get('okon').setDepth(.8)}}),
        new Wait({milliseconds:1000}),
        new Runner({name: "stop", func: (t)=>{t.blackboard.get('okon').setStableVel(null, null, 0, false);}}),
        new Wait({milliseconds:500}),
    ]}),
    new Selector({children:[
        new Sequence({name: "target gate", children:[
			new BooleanRunner({name: "calc target yaw", func: (t)=>{
				let okon = t.blackboard.get('okon');
				let hfov = 60;
				let detection = okon.getDetection('gate')
				if(detection.length === 1){
					let gate = detection[0];
					if(gate.distance < 1)return false;
					let center = (gate.max.x + gate.min.x)/2*2 - 1;
					let cameraPlaneX = 1.0/Math.tan(hfov/2/180*Math.PI)
					let deltaYaw = Math.atan(center/cameraPlaneX)/Math.PI*180;
					console.log('                                           mm',gate.max.x, gate.min.x);
					console.log('                                           center',center);
					console.log('                                           cameraPlaneX',cameraPlaneX);
					console.log('                                           deltaYaw',deltaYaw);
					t.blackboard.set('deltaYaw', deltaYaw);
					return true;
				}else return false;
			}}),
			new Runner({name: "setBB not visible 0", func: (t)=>t.blackboard.set('not-visible', 0)}),
			new DunamicRotate({variable: 'deltaYaw'}),
			new Runner({name: "move forward", func: (t)=>{t.blackboard.get('okon').setStableVel(null, null, .7, false);}}),
			new Wait({milliseconds:100}),
		]}),
		new Sequence({name: "check vis", children:[
			new Runner({name: "addBB not visible +1", func: (t)=>t.blackboard.set('not-visible', (t.blackboard.get('not-visible')||0) + 1)}),
			new BooleanRunner({name: "isBB not visible > 3", func: (t)=>t.blackboard.get('not-visible') > 3}),
		]}),
    ]}),
    new Sequence({name: "go through the gate", children: [
        new Wait({milliseconds:2000}),
        new Runner({name: "stop", func: (t)=>{t.blackboard.get('okon').setStableVel(null, null, 0, false);}}),
        new Runner({name: "end", func: (t)=>{throw 3}}),
    ]})
]})


let gateVisible2 = new Sequence({
	name: 'Gate Visible',
	children:[
		new Condition({ name: 'Gate Visible', condition: (tick)=>{
				let d = tick.blackboard.get('okon').sens.detection;
				for(let el of d){
					if(el.className == 'gate' && el.visibleInFrame){
						let gateMid = (el.min.x + el.max.x)/2;
						if(Math.abs(0.5 - gateMid) < 0.1)
						return true;
					}
				}
				return false;
			}
		}),
		new Runner({ name: 'Save gate ratio', func: (tick)=>{
				let d = tick.blackboard.get('okon').sens.detection;
				for(let el of d){
					if(el.className == 'gate' && el.visibleInFrame){
						tick.blackboard.set('firstGateRatio', (el.max.x-el.min.x)/(el.max.y-el.min.y));
						return;
					}
				}
			}
		}),
		new Sequence({ name: 'Strafe Right', children:[
				new Rotate({delta:90}),
				new GoForward({fill:.5}),
				new Wait({milliseconds:1000}),
				new GoForward({name:'Stop', fill:0}),
				new Rotate({delta:-90})
			]
		}),
		new Runner({ name: 'Compare gate ratio', func: (tick)=>{
				let d = tick.blackboard.get('okon').sens.detection;
				for(let el of d){
					if(el.className == 'gate' && el.visibleInFrame){
						tick.blackboard.set('gateLeftNearer', tick.blackboard.get('firstGateRatio') > (el.max.x-el.min.x)/(el.max.y-el.min.y));
						return;
					}
				}
			}
		}),
		new Condition({
			name: 'Gate Left is nearer',
			condition: (tick)=>{
				return tick.blackboard.get('gateLeftNearer');
			}
		})
	]
})

function exe(){
	//console.clear();
	process.stdout.write("\x1b[0;0H");
	process.stdout.write("\x1b[?25l");
	
	root.print('#      ', false, true, b); //DRAW TREE

    let t = new Tick({tree: {}, blackboard: b});
    let state = root.run(t);	
    //console.log(state);	
    //console.log(b.get('debug'));

	console.log("                                       ");
	console.log("                                       ");
	console.log("                                       ");
}
})();

process.on('SIGINT', (code) => {
    gokon.setStableVel(0,0,0)
	console.log(code);
	process.stdout.write("\x1b[?25h");
	console.log("terminated");
	process.exit();
});

