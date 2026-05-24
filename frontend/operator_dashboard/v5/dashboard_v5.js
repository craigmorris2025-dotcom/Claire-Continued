(async function(){
  try{
    const response=await fetch("/api/dashboard/v5/payload",{cache:"no-store"});
    await response.json();
  }catch(error){}
})();
