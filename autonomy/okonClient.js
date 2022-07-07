'use strict';
const EventEmitter = require('events');
const net = require('net');

const PacketType = {
	get : function (val) {
		for (let [key, value] of Object.entries(this))
		  if(value === val)return key;
	},
	SET_MTR : 0xA0,
	ARM_MTR : 0xA1,
	DISARM_MTR : 0xA2,
	SET_CONTROL_MODE : 0xA3,
	SET_ACRO : 0xA4,
	SET_STABLE : 0xA5,
	SET_PID : 0xA6,
	GET_SENS : 0xB0,
	GET_DEPTH : 0xB1,
	GET_DEPTH_BYTES : 0xB2,
	GET_VIDEO_BYTES : 0xB3,
	GET_VIDEO : 0xB4,
	SET_SIM : 0xC0,
	ACK : 0xC1,
	SET_ORIEN : 0xC3,
	RST_SIM : 0xC4,
	PING : 0xC5,
	GET_CPS : 0xC6,
	HIT_NGZ : 0xC7,
	HIT_FZ : 0xC8,
	CHK_AP : 0xC9,
	ERROR : 0xCA,
	REC_STRT : 0xD0,
	REC_ST : 0xD1,
	REC_RST : 0xD2,
	GET_REC : 0xD3,
	GET_DETE : 0xDE
}

const PacketFlag = {
	get : function (val) {
		if(val === 0) return "[NONE]";
		let flags = "<";
		for (let [key, value] of Object.entries(this)){
			if(!isNaN(value)){
				//console.log(key, value, val & value);
				if(val & value)flags += " " + key;
			}
		}
		return flags + ">";
	},
	 NONE : 0,
     SERVER_ECHO : 1,
     DO_NOT_LOG_PACKET : 2,
     TEST : 128
}

function angleDifference(angle1, angle2 ) {
    let diff = Math.abs(((angle1+360)%360) - ((angle2+360)%360));
    return Math.min(diff, 360 - diff);
}

function angle0360(angle) {
    return (angle % 360 + 360) % 360;
}

function angle180(angle){
	return angle > 180 ? angle-360 : angle;
}

function angleNorm(a){
	let x = angle180(angle0360(a.x));
	let y = angle180(angle0360(a.y));
	let z = angle180(angle0360(a.z));
	if(Math.abs(x) > 90){
		y = angle180(180 + y);
		x = angle180(angle0360(180 - x));
		z = angle180(angle0360(180 + z));
	}
	return {'x':x,'y':y,'z':z};
}

class MissionControl extends EventEmitter {
	constructor(okonClient){
		super();
		this.okonClient = okonClient;
		this.time = 60000;
		this.timer = null;
		this.successes = 0;
		this.fails = 0;
	}
	
	setTimer(time){
		if(time)this.time = time;
		if(this.timer)this.resetTimer();
		this.timer = setTimeout(()=>{
			this.fails++;
			this.emit('timer');
		}, time);
	}
	
	/*end(outcome){
		if(outcome > 0) this.fails++;
		if(outcome > 0) this.fails++;
	}*/
	
	resetTimer(){
		clearTimeout(this.timer);
		this.timer = null;
	}
	
	restart(){
		
	}
}

class Okon {
	constructor(okonClient){
		this.okonClient = okonClient;
		this.sens = {
			imu: {
				rot : {x: 0, y: 0, z: 0},
				rotSpeed : {x: 0, y: 0, z: 0},
				rotAccel : {x: 0, y: 0, z: 0},
				accel : {x: 0, y: 0, z: 0}
			},
			baro : 0,
			detection : []
		};
		this.peripherals = {
			motors: { /* TODO */},
			ligths: { },
			arms: { }
		}
		this.control = {
			mode: 'unknown',
			stable: {
				targetRot: {x: 0, y: 0, z: 0},
				vel: {x: 0, y: 0, z: 0},
				targetDepth: 1.3
			},
			acro: {
				rotSpeed: {x: 0, y: 0, z: 0},
				vel: {x: 0, y: 0, z: 0}
			}
		};
		this.orien = {
			pos : {x: 0, y: 0, z: 0},
			rot : {x: 0, y: 0, z: 0}
		}
/*

- mode

  - stable
    - setRot
	- setStableVel
	- setDepth
  - acro
    - setRotSpeed
	- setAcroVel
*/
	}
	
	reachedTargetRotation(delta){
		return angleDifference(this.control.stable.targetRot.x, this.sens.imu.rot.x) < delta &&
			 angleDifference(this.control.stable.targetRot.y, this.sens.imu.rot.y) < delta &&
			 angleDifference(this.control.stable.targetRot.z, this.sens.imu.rot.z) < delta;
	}
	
	reachedTargetDepth(delta){
		return Math.abs(this.control.stable.targetDepth + this.orien.pos.y) < delta;
	}
	
	armMotors(){
		this.okonClient.send(PacketType.ARM_MTR, PacketFlag.NONE);
	}
	
	disarmMotors(){
		this.okonClient.send(PacketType.DISARM_MTR, PacketFlag.NONE);
	}
	
	reset(){
		this.control.stable = {
			targetRot: {x: 0, y: 0, z: 0},
			vel: {x: 0, y: 0, z: 0},
			targetDepth: 1
		};
		this.okonClient.send(PacketType.SET_STABLE,PacketFlag.DO_NOT_LOG_PACKET,JSON.stringify({
			rot:this.control.stable.targetRot,
			vel: this.control.stable.vel,
			depth: this.control.stable.targetDepth
		}));
	}
	
	getDetection(className){
		return this.sens.detection.filter(d => d.className === className && d.visibleInFrame);
		//for(let d of this.sens.detection) if(d.className === className && d.visibleInFrame) return d;
	}
	
	setPID(name, parameter, val, stack){
		val = Number(val);
		if(this.pids && this.pids[name] && !isNaN(this.pids[name][parameter])){
			if(stack)this.pids[name][parameter] += val;
			else this.pids[name][parameter] = val;
			this.okonClient.send(PacketType.SET_PID, PacketFlag.NONE, JSON.stringify(this.pids));
		}
	}
	
	setRot(x, y, z, add){
		if(add){
			if(!(x == null))this.control.stable.targetRot.x += x;
			if(!(y == null))this.control.stable.targetRot.y += y;
			if(!(z == null))this.control.stable.targetRot.z += z;
		}else{
			if(!(x == null))this.control.stable.targetRot.x = x;
			if(!(y == null))this.control.stable.targetRot.y = y;
			if(!(z == null))this.control.stable.targetRot.z = z;
		}
		this.control.stable.targetRot = angleNorm(this.control.stable.targetRot);
		this.okonClient.send(PacketType.SET_STABLE,PacketFlag.DO_NOT_LOG_PACKET,JSON.stringify({
			rot:this.control.stable.targetRot,
			vel: this.control.stable.vel,
			depth: this.control.stable.targetDepth
		}));
	}
	
	setRotSpeed(x, y, z, add){//TODO
		if(add){
			if(!(x == null))this.control.acro.rotSpeed.x += x;
			if(!(y == null))this.control.acro.rotSpeed.y += y;
			if(!(z == null))this.control.acro.rotSpeed.z += z;
		}else{
			if(!(x == null))this.control.acro.rotSpeed.x = x;
			if(!(y == null))this.control.acro.rotSpeed.y = y;
			if(!(z == null))this.control.acro.rotSpeed.z = z;
		}
		this.control.acro.rotSpeed = angleNorm(this.control.acro.rotSpeed);
		this.okonClient.send(PacketType.SET_ACRO,PacketFlag.DO_NOT_LOG_PACKET,JSON.stringify({
			rot:this.control.acro.rotSpeed,
			vel: this.control.acro.vel
		}));
	}
	
	setStableVel(x, y, z, add){
		if(add){
			if(!(x == null))this.control.stable.vel.x += x;
			if(!(y == null))this.control.stable.vel.y += y;
			if(!(z == null))this.control.stable.vel.z += z;
		}else{
			if(!(x == null))this.control.stable.vel.x = x;
			if(!(y == null))this.control.stable.vel.y = y;
			if(!(z == null))this.control.stable.vel.z = z;
		}
		this.okonClient.send(PacketType.SET_STABLE,PacketFlag.DO_NOT_LOG_PACKET,JSON.stringify({
			rot:this.control.stable.targetRot,
			vel: this.control.stable.vel,
			depth: this.control.stable.targetDepth
		}));
	}
	
	setAcroVel(x, y, z, add){
		if(add){
			if(!(x == null))this.control.acro.vel.x += x;
			if(!(y == null))this.control.acro.vel.y += y;
			if(!(z == null))this.control.acro.vel.z += z;
		}else{
			if(!(x == null))this.control.acro.vel.x = x;
			if(!(y == null))this.control.acro.vel.y = y;
			if(!(z == null))this.control.acro.vel.z = z;
		}
		this.okonClient.send(PacketType.SET_ACRO,PacketFlag.DO_NOT_LOG_PACKET,JSON.stringify({
			rot_speed:this.control.acro.targetRot,
			vel: this.control.acro.vel
		}));
	}
	
	setDepth(depth, add){
		if(add) this.control.stable.targetDepth += depth; 
		else this.control.stable.targetDepth = depth; 
		this.okonClient.send(PacketType.SET_STABLE,PacketFlag.DO_NOT_LOG_PACKET,JSON.stringify({
			rot:this.control.stable.targetRot,
			vel: this.control.stable.vel,
			depth: this.control.stable.targetDepth
		}));
	}
	
	setMode(mode){
		this.control.mode = mode;
		this.okonClient.send(PacketType.SET_CONTROL_MODE, PacketFlag.NONE, mode);
	}
	
	setRawMotors(/*motors object or args*/){
		//TODO GET SET packet to update or add
	}
}

class Simulation extends EventEmitter {
	constructor(okonClient){
		super();
		this.okonClient = okonClient;
		this.checkpoints = [];
	}
	
	reset(){
		this.okonClient.send(PacketType.RST_SIM, PacketFlag.NONE);
		this.okonClient.send(PacketType.DISARM_MTR, PacketFlag.NONE);
		this.okonClient.okon.reset();
	}
	
	sync(){
		this.okonClient.send(PacketType.SET_ORIEN, PacketFlag.DO_NOT_LOG_PACKET);
		this.okonClient.send(PacketType.GET_SENS, PacketFlag.DO_NOT_LOG_PACKET);
		this.okonClient.send(PacketType.SET_PID, PacketFlag.DO_NOT_LOG_PACKET);
		this.okonClient.send(PacketType.SET_CONTROL_MODE, PacketFlag.DO_NOT_LOG_PACKET);
		this.okonClient.send(PacketType.SET_STABLE, PacketFlag.DO_NOT_LOG_PACKET);
		this.okonClient.send(PacketType.GET_DETE, PacketFlag.DO_NOT_LOG_PACKET);
	}
}

class OkonClient extends EventEmitter {
	constructor(ip, port, options){ // if('customOption' in options){}
		super();
		this.options = options || {};
		
		this.simulation = new Simulation(this);
		this.okon = new Okon(this);
		this.missionControl = new MissionControl(this);
		
		this.ip = ip;
		this.port = port;
		this.socket = new net.Socket();
		this.receiveBuffer = Buffer.alloc(0,0),
		this.waitingForPacket = true;
		this.type = null;
		this.flag = null;
		this.len = null;
		this.socket.on("data", (data)=>{
			this.receiveBuffer = Buffer.concat([this.receiveBuffer, Buffer.from(data)]);
			while((this.waitingForPacket && this.receiveBuffer.length >= 6) || (!this.waitingForPacket && this.receiveBuffer.length >= this.len)){
				if(this.waitingForPacket){
					if(this.receiveBuffer.length >= 6){
						this.type = this.receiveBuffer.readUInt8(0);
						this.flag = this.receiveBuffer.readUInt8(1);
						this.len =  this.receiveBuffer.readUint32LE(2);
						this.receiveBuffer = this.receiveBuffer.slice(6);
						this.waitingForPacket = false;
					}
				} 
				if(!this.waitingForPacket){
					let jsonData = null;
					if(this.receiveBuffer.length >= this.len){
						jsonData = this.receiveBuffer.slice(0, this.len).toString('ascii');
						this.receiveBuffer = this.receiveBuffer.slice(this.len);
						this.waitingForPacket = true;
						const p = {type: this.type, flag: this.flag, json: jsonData};
						this.handleInfoPacket(p);
					}
				}
			}
		});
		this.socket.on('close', () => {
			console.log('connection closed');
			this.connected = false;
		});
	}
	
	handleInfoPacket(p){
		if(this.options.SHOW_PACKET_TIME)console.log('R', Date.now()-this.startTime,PacketType.get(p.type), p.json.length, p.json.substr(0,100));
		switch(p.type){
			case PacketType.RST_SIM:
				this.simulation.emit('reset');
				break;
			case PacketType.SET_PID:
				this.okon.pids = JSON.parse(p.json);
				break;
			case PacketType.SET_STABLE:
				let stable = JSON.parse(p.json);
				this.okon.control.stable.targetRot = stable.rot;
				this.okon.control.stable.targetDepth = stable.depth;
				this.okon.control.stable.vel = stable.vel;
				break;
			case PacketType.GET_SENS:
				let sens = JSON.parse(p.json);
				sens.rot = angleNorm(sens.rot);
				this.okon.sens.baro = sens.baro.pressure;
				this.okon.sens.imu = sens;
				break;
			case PacketType.GET_DEPTH:
				console.log('depth base64', p.json.length, '\n', p.json, '\n');
				break;
			case PacketType.GET_VIDEO:
				console.log('video base64', p.json.length, '\n', p.json, '\n');
				break;
			case PacketType.SET_ORIEN:
				let orien = JSON.parse(p.json);
				this.okon.orien.pos = orien.pos;
				this.okon.orien.rot = angleNorm(orien.rot);
				break;
			case PacketType.SET_CONTROL_MODE:
				this.okon.control.mode = p.json;
				break;
			case PacketType.ACK:
				if(p.json) console.log(JSON.parse(p.json));
				break;
			case PacketType.ERROR:
				console.log(JSON.parse(p.json));
				break;
			case PacketType.GET_DETE:
				this.okon.sens.detection = JSON.parse(p.json);
				break;
			case PacketType.GET_CPS:
				this.simulation.checkpoints = JSON.parse(p.json);
				break;
			case PacketType.HIT_NGZ:
				this.simulation.emit('hitNGZ', p.json);
				break;
			case PacketType.HIT_FZ:
				this.simulation.emit('hitFZ', p.json);
				break;
			default:
				if(!(p.flag & PacketFlag.DO_NOT_LOG_PACKET))this.emit('packet', p);
		}
	}
	
	connect(){
		this.socket.connect(this.port, this.ip, ()=>{
			this.connected = true;
			this.startTime = Date.now();
			this.simulation.sync();
			if(this.options.GET_DETE)setInterval(()=>this.send(PacketType.GET_DETE,PacketFlag.DO_NOT_LOG_PACKET), this.options.GET_DETE);
			if(this.options.GET_CPS)setInterval(()=>this.send(PacketType.GET_CPS,PacketFlag.DO_NOT_LOG_PACKET), this.options.GET_CPS);
			if(this.options.SET_ORIEN)setInterval(()=>this.send(PacketType.SET_ORIEN,PacketFlag.DO_NOT_LOG_PACKET), this.options.SET_ORIEN);
			if(this.options.GET_SENS)setInterval(()=>this.send(PacketType.GET_SENS,PacketFlag.DO_NOT_LOG_PACKET), this.options.GET_SENS);
			if(this.options.TOTAL_SYNC)setInterval(()=>this.simulation.sync(), this.options.TOTAL_SYNC);
			setTimeout(()=>this.emit('connected'), 50);
		});
	}
	
	disconnect(){
		this.connected = false;
		this.socket.end();
		this.socket.destroy();
		this.emit('disconnected');
	}
	
	send(type, flag, data){
		if(!this.connected)return;
		if(this.options.SHOW_PACKET_TIME)console.log('S', Date.now()-this.startTime,PacketType.get(type), data);
		let b = Buffer.alloc(6);
		b.writeUInt8(type, 0);
		b.writeUInt8(flag, 1);
		b.writeUInt32LE(data ? data.length : 0, 2);
		if(data)b = Buffer.concat([b, Buffer.from(data, 'ascii')]);
		this.socket.write(b);
	}
}
	
module.exports.PacketType = PacketType;
module.exports.PacketFlag = PacketFlag;
module.exports.OkonClient = OkonClient;