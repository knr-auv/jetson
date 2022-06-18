export default class Tick{
	static id = 0;
	constructor({tree, blackboard}={}){
		this.id = Tick.id++;
		this.tree = tree;
		this.blackboard = blackboard;
		this.loadedNodes = [];
		this.loadedNodesNum = 0;
	}
	
	loadNode(node){
		this.loadedNodes.push(node);
		this.loadedNodesNum++;
	}
	
	leaveNode(node){
		this.loadedNodes.pop();
	}
}