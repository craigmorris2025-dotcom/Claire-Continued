(async function(){
  async function loadContract(){
    const response=await fetch("/dashboard/operator-console/contract",{method: "GET",cache:"no-store"});
    return response.json();
  }
  try{
    const payload=await loadContract();
    window.claireOperatorConsoleContract=payload;
    console.info("No web execution; runtime mutation blocked; command execution blocked");
  }catch(error){
    console.info("No web execution; runtime mutation blocked; command execution blocked");
  }
})();
