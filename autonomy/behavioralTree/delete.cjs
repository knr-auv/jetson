(async ()=>{
const {default: Node} = await import('./Node.mjs');
console.log(new Node());
})();