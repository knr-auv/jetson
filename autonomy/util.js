'use strict';
const {OkonClient, PacketType, PacketFlag} = require('./okonClient');
const {ActionNode} = require('./actionTree');
const fs = require('fs');

let okonClient = new OkonClient('127.0.0.1', '44210', {SHOW_PACKET_TIME:false});
let {okon, simulation, missionControl} = okonClient;

function getArg(arg){
	return arg.includes('=') ? [Number(arg.substr(1)), false] : [Number(arg), true];
}

okonClient.on('connected', ()=>{
	console.log('connected');
	let args = process.argv.slice(2);
	
	start.execute({'argv':args});
	setTimeout(()=>{
		okonClient.disconnect();
		setTimeout(()=>{
			process.exit();
		},50);
	},50);
	console.log('conn event end');
});

let simSync = new ActionNode('sync', [], (ed)=>ed.argv[1] === 'sync', (ed)=>simulation.sync());
let simReset = new ActionNode('reset', [], (ed)=>ed.argv[1] === 'reset', (ed)=>okonClient.send(PacketType.RST_SIM, PacketFlag.NONE));
let sim = new ActionNode('simulation', [simReset, simSync], (ed)=>ed.argv[0] === 'simulation', (ed)=>console.log('sim'));
let send = new ActionNode('send', [], (ed)=>ed.argv[0] === 'send' && ed.argv.length >= 2 && ed.argv.length <= 3, (ed)=>okonClient.send(Number(ed.argv[1]), PacketFlag.NONE, ed.argv[2]));
let detectionAspectRatio = new ActionNode('detection', [], (ed)=>ed.argv[1] === 'ratio', (ed)=>{
		console.log('okon.sens.detection', okon.sens.detection.map((o)=>{ return { className : o.className, aspectRatio: (o.max.x-o.min.x)/(o.max.y-o.min.y) }; }));
});
let detection = new ActionNode('detection', [detectionAspectRatio], (ed)=>ed.argv[0] === 'detection', (ed)=>console.log('okon.sens.detection',okon.sens.detection));
let depthChange = new ActionNode('depth', [], (ed)=>ed.argv[1] != undefined, (ed)=>{
	console.log('old', 'okon.control.stable.targetDepth', okon.control.stable.targetDepth);
	okon.setDepth(getArg(ed.argv[1])[0], getArg(ed.argv[1])[1]);
	console.log('new', 'okon.control.stable.targetDepth', okon.control.stable.targetDepth);
});
let depth = new ActionNode('depth', [depthChange], (ed)=>ed.argv[0] === 'depth', (ed)=>console.log('okon.control.stable.targetDepth', okon.control.stable.targetDepth));
let modeChange = new ActionNode('change', [], (ed)=>ed.argv.length === 2, (ed)=>{
	console.log('old', 'okon.control.mode', okon.control.mode);
	okon.setMode(ed.argv[1]);
	console.log('new', 'okon.control.mode', okon.control.mode);
});
let mode = new ActionNode('mode', [modeChange], (ed)=>ed.argv[0] === 'mode', ()=>console.log('okon.control.mode', okon.control.mode));
let pidChange = new ActionNode('change', [], (ed)=>ed.argv.length === 4 && okon.pids[ed.argv[1]] && !isNaN(okon.pids[ed.argv[1]][ed.argv[2]]), (ed)=>{
	console.log('old', 'okon.pids.'+ed.argv[1]+'.'+ed.argv[2], okon.pids[ed.argv[1]][ed.argv[2]]);
	okon.setPID(ed.argv[1], ed.argv[2], getArg(ed.argv[3])[0], getArg(ed.argv[3])[1]);
	console.log('new', 'okon.pids.'+ed.argv[1]+'.'+ed.argv[2], okon.pids[ed.argv[1]][ed.argv[2]]);
});
let pid = new ActionNode('pid', [pidChange], (ed)=>ed.argv[0] === 'pid', ()=>console.log('okon.pids', okon.pids));
let rotChange = new ActionNode('change', [], (ed)=>ed.argv.length === 3, (ed)=>{
	console.log('okon.control.stable', okon.control.stable.targetRot);
	let axis = ed.argv[1];
	let val = getArg(ed.argv[2])[0];
	let x, y, z;
	if(axis === 'x' || axis === 'pitch') x = val;
	if(axis === 'y' || axis === 'yaw') y = val;
	if(axis === 'z' || axis === 'roll') z = val;
	okon.setRot(x, y, z, getArg(ed.argv[2])[1]);
	console.log('okon.control.stable', okon.control.stable.targetRot);
});
let rot = new ActionNode('rot', [rotChange], (ed)=>ed.argv[0] === 'rot', ()=>console.log('okon.control.stable', okon.control.stable.targetRot));
let velChange = new ActionNode('change', [], (ed)=>ed.argv.length === 3, (ed)=>{
	console.log('old','okon.control.stable.vel', okon.control.stable.vel);
	let axis = ed.argv[1];
	let val = getArg(ed.argv[2])[0];
	let x, y, z;
	if(axis === 'x') x = val;
	if(axis === 'y') y = val;
	if(axis === 'z') z = val;
	okon.setStableVel(x, y, z, getArg(ed.argv[2])[1]);
	console.log('new', 'okon.control.stable.vel', okon.control.stable.vel);
});
let vel = new ActionNode('vel', [velChange], (ed)=>ed.argv[0] === 'vel', ()=>console.log('okon.control.stable.vel', okon.control.stable.vel));

let start = new ActionNode('util', [sim, send, detection, depth, mode, pid, rot, vel], null, ()=>console.log('help:'));

console.log('connecting...');
okonClient.connect();

/*
sim reset
okon orien

okon mode manual/stable/acro
okon stable rot 
okon stable rot x +10
okon stable rot x =+10
okon stable rot x -10
okon stable rot x =-10
okon stable rot y _10
okon stable rot xyz 0 =-20 -20
okon arm/disarm
okon sens 
okon orien
okon orien rot
okon orien pos 
okon orien pos 

start
├pid
│├roll
││├p
││├i
││├d
││├k
││└l
│├pitch
│└yaw
└rot
*/