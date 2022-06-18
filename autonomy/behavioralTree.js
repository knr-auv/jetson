'use strict';
function consolelog(...x){
	for(let i = 0; i < x.length; i++){
		process.stdout.write(x[i]);
		process.stdout.write(" ");
	}
	process.stdout.write("                     \n");
}
console.clear();
(async ()=>{
const {OkonClient, PacketType, PacketFlag} = require('./okonClient');
const {Wait, Blackboard, Tick, Action, InterruptSelector,InterruptSequence, Decorator, Sequence, Condition, Selector} = await import('./behavioralTree/BT.mjs');
const fs = require('fs');
const gamepad = require("gamepad");

let okonClient = new OkonClient('127.0.0.1', '44210', {SHOW_PACKET_TIME:false,TOTAL_SYNC:50, GET_CPS:500});
let {okon, simulation, missionControl} = okonClient;

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
/*

 

*/
/*new InterruptSelector({
	children:[
		new Sequence({
			children:[
				new Condition({
					name: 'Gate Visible',
					condition: (tick)=>{
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
				new Rotate({delta:180}),
				new Wait({milliseconds:1000})
			]
		}),
		new Sequence({
			children:[
				new Rotate({name:'Rotate <delta> degrees', delta:5}),
				new Wait({milliseconds:100})
			]
		})
	]
});*/

let aiEnabled = false;
gamepad.init()
setInterval(gamepad.processEvents, 16);
setInterval(gamepad.detectDevices, 500);

const pad = {
	LT:0,LB:false,RT:0,RB:false,
	LX:0,LY:0,RX:0,RY:0,L:false,R:false,
	DL:false,DU:false,DD:false,DR:false,
	SELECT:false,START:false,
	X:false,Y:false,A:false,B:false,
	XBOX:false,
	print: function(){
		let tr = "";
		for(let el in this)if(this[el] === true)tr+=el+' ';
		console.log(tr);
		console.log(this.LX.toFixed(1), this.LY.toFixed(1), this.RX.toFixed(1), this.RY.toFixed(1));
		console.log(this.LT.toFixed(2), this.RT.toFixed(2));
	}
};

//console.log(pad);

gamepad.on("move", function (id, axis, value) {
  if(axis === 0)pad.LX = value;
  else if(axis === 1)pad.LY = value;
  else if(axis === 2)pad.RX = value;
  else if(axis === 3)pad.RY = value;
  else if(axis === 4)pad.LT = (value+1)/2;
  else if(axis === 5)pad.RT = (value+1)/2;
});
 
gamepad.on("down", function (id, num) {
  if(num === 0)pad.DU = true;
  else if(num === 1)pad.DD = true;
  else if(num === 2)pad.DL = true;
  else if(num === 3)pad.DR = true;
  else if(num === 4){
	  pad.START = true;
	  okon.setRot(null, okon.sens.imu.rot.y, null);
	  okon.armMotors();
  }
  else if(num === 5)pad.SELECT = true;
  else if(num === 6)pad.L = true;
  else if(num === 7)pad.R = true;
  else if(num === 8)pad.LB = true;
  else if(num === 9)pad.RB = true;
  else if(num === 10){
	  aiEnabled = !aiEnabled;
	  pad.A = true;
  }
  else if(num === 11)pad.B = true;
  else if(num === 12)pad.X = true;
  else if(num === 13)pad.Y = true;
  else if(num === 14){
	  simulation.reset();
	  pad.XBOX = true;
  }
});
 
gamepad.on("up", function (id, num) {
  if(num === 0)pad.DU = false;
  if(num === 1)pad.DD = false;
  if(num === 2)pad.DL = false;
  if(num === 3)pad.DR = false;
  if(num === 4)pad.START = false;
  if(num === 5){
	  okon.disarmMotors();
	  pad.SELECT = false;
  }
  if(num === 6)pad.L = false;
  if(num === 7)pad.R = false;
  if(num === 8)pad.LB = false;
  if(num === 9)pad.RB = false;
  if(num === 10)pad.A = false;
  if(num === 11)pad.B = false;
  if(num === 12)pad.X = false;
  if(num === 13)pad.Y = false;
  if(num === 14)pad.XBOX = false;
});

function exe(){
	//console.clear();
	process.stdout.write("\x1b[0;0H");
	process.stdout.write("\x1b[?25l");
	
	root.print('#      ', false, true, b); //DRAW TREE
	if(aiEnabled){
		let t = new Tick({tree: {}, blackboard: b});
		let state = root.run(t);	
		//console.log(state);	
		//console.log(b.get('debug'));
	}else{
		pad.print();
		okon.setStableVel(Math.abs(pad.LX) > 0.1 ? pad.LX : 0, null, Math.abs(pad.LY) > 0.1 ? pad.LY : 0, false);
		if(okon.reachedTargetRotation(10))okon.setRot(null, Math.abs(pad.RX) > 0.1 ? pad.RX*10 : 0, null, true);
		if(okon.reachedTargetDepth(0.05))okon.setDepth(pad.LB?0.1:pad.RB?-0.1:0,true);
		if(pad.B){
			okon.setRot(null, okon.sens.imu.rot.y, null);
			okon.setDepth(-okon.orien.pos.y);
		}
	}
	console.log("                                       ");
	console.log("                                       ");
	console.log("                                       ");
}


})();

process.on('SIGINT', (code) => {
	console.log(code);
	process.stdout.write("\x1b[?25h");
	console.log("terminated");
	process.exit();
});

/*
https://www.csc.kth.se/~miccol/Michele_Colledanchise/Publications_files/2013_ICRA_mcko.pdf <<<
https://robohub.org/introduction-to-behavior-trees/ <<
https://www.gamecareerguide.com/features/1405/using_behavior_trees_to_create_.php <<<
https://www.gamedeveloper.com/programming/behavior-trees-for-ai-how-they-work <
https://robohub.org/introduction-to-behavior-trees/ <<<
https://opensource.adobe.com/behavior_tree_editor/#/editor <<<
https://cdn.discordapp.com/attachments/675801390886551552/906879064009236480/unknown.png KNR
https://www.youtube.com/watch?v=sETuC2Mr6D8&list=PLFQdM4LOGDr_vYJuo8YTRcmv3FrwczdKg&index=7
https://www.gameaipro.com/GameAIPro/GameAIPro_Chapter06_The_Behavior_Tree_Starter_Kit.pdf
https://web.archive.org/web/20150626035025/http://docs.guineashots.com/behavior3js/classes/Wait.html
https://www.youtube.com/watch?v=SgrG6uAZDHE	
*/