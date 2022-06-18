export default class Blackboard{
	constructor({}={}){
		this.globalData = {};
		this.nodeData = {};
	}
	
	set(key, val, nodeID){
		if(key == null)return;
		if(nodeID != null){
			if(!this.nodeData[nodeID])this.nodeData[nodeID] = {};
			this.nodeData[nodeID][key] = val;
		}else{
			this.globalData[key] = val;
		}
	}
	
	get(key, nodeID){
		if(key == null)return undefined;
		if(nodeID != null){
			if(!this.nodeData[nodeID])return undefined;
			return this.nodeData[nodeID][key];
		}else{
			return this.globalData[key];
		}
	}
}